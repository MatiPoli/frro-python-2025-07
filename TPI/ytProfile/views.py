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
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        load_subscriptions(request)

        subs_db = Subscription.objects.filter(usuario=request.user).select_related('canal').prefetch_related('canal__categorias')
        subscriptions_render = []
        all_topics = []
        for sub in subs_db:
            categorias = list(sub.canal.categorias.all())
            if categorias:
                topics = [cat.tematica for cat in categorias]
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
        chart_data = json.dumps([
            {'category': k, 'count': v} for k, v in topic_distribution.items()
        ])

        followers_count = 10
        following_count = 15

        context = {
            'username': request.user.username,
            'followers_count': followers_count,
            'following_count': following_count,
            'subscriptions_count': subs_db.count(),
            'subscriptions': subscriptions_render,
            'topic_distribution': chart_data,
        }

        return render(request, 'profile2.html', context)

    except HttpError as e:
        print(f"Error de HTTP: {e.resp.status}")
        return HttpResponseRedirect(reverse('error_page')) 
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return HttpResponseRedirect(reverse('error_page'))