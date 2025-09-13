import os
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from collections import defaultdict
import json
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
from authentication.utils import get_youtube_service, load_subscriptions

import os
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from django.shortcuts import render
from collections import Counter

from ytProfile.models import Subscription


def error_view(request):
    return render(request, 'error.html')

def profile_view(request):
    # Obtener foto de Google del usuario
    from allauth.socialaccount.models import SocialAccount
    google_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
    google_photo = None
    if google_account and 'picture' in google_account.extra_data:
        google_photo = google_account.extra_data['picture']
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        load_subscriptions(request)

        subs_db = Subscription.objects.filter(usuario=request.user).select_related('canal').prefetch_related('canal__categorias')
        subscriptions_render = []
        all_topics = []
        import re
        for sub in subs_db:
            categorias = list(sub.canal.categorias.all())
            if categorias:
                topics = [re.sub(r"\s*\(.*?\)", "", cat.tematica).strip() for cat in categorias]
                all_topics.extend(topics)
                topic_str = ', '.join(topics)
            else:
                topic_str = 'Sin categoría'
                all_topics.append(topic_str)
            subscriptions_render.append({
                'title': sub.canal.nombreCanal,
                'topic': topic_str,
                'thumbnail_url': sub.canal.thumbnail_url
            })

        topic_distribution = Counter(all_topics)
        total = sum(topic_distribution.values())
        chart_data_list = []
        otras_count = 0
        import re
        from ytProfile.models import Categoria
        for k, v in topic_distribution.items():
            # Eliminar todo lo que esté entre paréntesis y espacios extra
            main_cat = re.sub(r"\s*\(.*?\)", "", k).strip()
            percent = (v / total) * 100 if total > 0 else 0
            if percent < 2:
                otras_count += v
            else:
                # Buscar color en la BD
                try:
                    cat_obj = Categoria.objects.get(tematica=main_cat)
                    print("DEBUG:", cat_obj)
                    color = cat_obj.color
                    
                except Categoria.DoesNotExist:
                    color = "#b0b0b0"
                chart_data_list.append({'category': main_cat, 'count': v, 'color': color})
        if otras_count > 0:
            chart_data_list.append({'category': 'Otras', 'count': otras_count, 'color': '#b0b0b0'})
  
            chart_data = json.dumps(chart_data_list)

        from ytProfile.models import Follow
        followers_count = Follow.objects.filter(seguido=request.user).count()
        following_count = Follow.objects.filter(seguidor=request.user).count()

        context = {
            'username': request.user.username,
            'followers_count': followers_count,
            'following_count': following_count,
            'subscriptions_count': subs_db.count(),
            'subscriptions': subscriptions_render,
            'topic_distribution': chart_data,
            'google_photo': google_photo,
        }

        return render(request, 'profile2.html', context)

    except HttpError as e:
        print(f"Error de HTTP: {e.resp.status}")
        return HttpResponseRedirect(reverse('error_page')) 
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return HttpResponseRedirect(reverse('error_page'))