import os
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect
from googleapiclient.errors import HttpError

from authentication.utils import load_subscriptions
from .models import Follow
from .services import get_profile_data
from ytRecommendation.services import get_channel_recommendations
from allauth.socialaccount.models import SocialAccount

def error_view(request):
    return render(request, 'error.html')

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        # Actualizar suscripciones desde la API de YouTube
        load_subscriptions(request)

        # 1. Obtener todos los datos del perfil desde el nuevo servicio
        profile_data = get_profile_data(request.user)

        # 2. Obtener datos de seguidores/seguidos
        followers_count = Follow.objects.filter(seguido=request.user).count()
        following_count = Follow.objects.filter(seguidor=request.user).count()

        # 3. Obtener foto de perfil de Google
        google_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
        google_photo = google_account.extra_data.get('picture') if google_account else None

        # 4. Obtener recomendaciones (pasando la distribución de temas que ya calculamos)
        recommendations = get_channel_recommendations(request.user, profile_data['topic_distribution'])

        # 5. Construir el contexto para la plantilla
        context = {
            'username': request.user.username,
            'google_photo': google_photo,
            'followers_count': followers_count,
            'following_count': following_count,
            'subscriptions_count': profile_data['subscriptions_count'],
            'subscriptions': profile_data['subscriptions_render'],
            'topic_distribution': profile_data['chart_data'],
            'recommendations': recommendations,
        }

        return render(request, 'profile2.html', context)

    except HttpError as e:
        print(f"Error de HTTP: {e.resp.status}")
        return HttpResponseRedirect(reverse('error_page')) 
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return HttpResponseRedirect(reverse('error_page'))
