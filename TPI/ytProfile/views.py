def poblar_categorias_youtube(request):
    """
    esto es una funcioncita q use una vez para meter las categorias
    se accede por una url yt/poblar-categorias/
    igual por alguna razon me crea solo 12
    Pobla la tabla Categoria con todas las categorías oficiales de YouTube usando la API y la autenticación del usuario.
    """
    if not request.user.is_authenticated:
        return HttpResponse("No autenticado", status=401)
    from .models import Categoria
    youtube = get_youtube_service(request.user)
    try:
        response = youtube.videoCategories().list(
            part='snippet',
            regionCode='AR'
        ).execute()
        creadas = 0
        for item in response.get('items', []):
            if item['snippet'].get('assignable', False):
                cat_id = item['id']
                title = item['snippet']['title']
                obj, created = Categoria.objects.get_or_create(id=cat_id, defaults={'tematica': title})
                if created:
                    creadas += 1
        return HttpResponse(f"Categorías creadas: {creadas}")
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)
    

# profile_views.py
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
from authentication.utils import get_youtube_service

import os
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# At the end of your imports in ytProfile/views.py
from django.shortcuts import render

# ... other views

def error_view(request):
    """A simple view to display an error page."""
    return render(request, 'error.html')

# Desactiva la advertencia de transporte inseguro si estás probando localmente
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# El scope (alcance) necesario para acceder a las suscripciones del usuario autenticado
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
CLIENT_SECRETS_FILE = 'client_secret.json'  # Asegúrate de que este archivo esté en la misma carpeta






"""
def profile_view(request):
    return HttpResponse("<h1>Esta es la página de perfil</h1>")
"""

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        #return render(request, 'profile2.html')
        youtube = get_youtube_service(request.user)
        from .models import Categoria, Canal, Subscription

        subscriptions_list = get_subscriptions_with_details(youtube)

        # Poblar la base de datos con las suscripciones del usuario
        for sub in subscriptions_list:
            # Categoria
            categoria_obj, _ = Categoria.objects.get_or_create(tematica=sub['topic'])
            # Canal: obtener thumbnail_url si está disponible en sub
            thumbnail_url = sub.get('thumbnail_url')
            canal_obj, created = Canal.objects.get_or_create(
                idCanal=sub['channel_id'],
                defaults={
                    'nombreCanal': sub['title'],
                    'categoria': categoria_obj,
                    'thumbnail_url': thumbnail_url
                }
            )
            # Si el canal ya existe pero no tiene thumbnail_url, actualizarlo
            if not canal_obj.thumbnail_url and thumbnail_url:
                canal_obj.thumbnail_url = thumbnail_url
                canal_obj.save()
            # Actualizar categoria si el canal ya existe pero no tiene
            if canal_obj.categoria is None:
                canal_obj.categoria = categoria_obj
                canal_obj.save()
            # Subscription
            Subscription.objects.get_or_create(
                usuario=request.user,
                canal=canal_obj
            )

        # Obtener las suscripciones guardadas del usuario
        subs_db = Subscription.objects.filter(usuario=request.user).select_related('canal__categoria')
        subscriptions_render = [
            {
                'title': sub.canal.nombreCanal,
                'topic': sub.canal.categoria.tematica if sub.canal.categoria else 'Sin categoría',
                'thumbnail_url': sub.canal.thumbnail_url
            }
            for sub in subs_db
        ]

        # Calcular la distribución para el gráfico
        from collections import Counter
        topic_distribution = Counter([sub['topic'] for sub in subscriptions_render])
        chart_data = json.dumps([
            {'category': k, 'count': v} for k, v in topic_distribution.items()
        ])

        # Datos de ejemplo para seguidores y seguidos (puedes conectar con el modelo Follow si lo deseas)
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
        return HttpResponseRedirect(reverse('error_page')) # Asume que hay una vista 'error_page'
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return HttpResponseRedirect(reverse('error_page'))



def get_subscriptions_with_details(youtube_service):
    """
    Obtiene las suscripciones del usuario, junto con los detalles de cada canal
    para extraer información como las categorías (topics).
    """
    subscriptions = []
    next_page_token = None

    while True:
        # Obtiene las suscripciones del usuario
        request = youtube_service.subscriptions().list(
            part='snippet',
            mine=True,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        channel_ids = [item['snippet']['resourceId']['channelId'] for item in response.get('items', [])]

        # Para cada grupo de suscripciones, obtén los detalles del canal
        if channel_ids:
            channels_request = youtube_service.channels().list(
                part='snippet,topicDetails',
                id=','.join(channel_ids)
            )
            channels_response = channels_request.execute()

            channels_details = {item['id']: item for item in channels_response.get('items', [])}

            for item in response.get('items', []):
                channel_id = item['snippet']['resourceId']['channelId']
                channel_details = channels_details.get(channel_id, {})

                # Extrae los temas principales del canal (o una categoría por defecto)
                topics = channel_details.get('topicDetails', {}).get('topicCategories', ['Sin categoría'])
                # Formatea el nombre de la categoría para que sea más legible
                primary_topic = topics[0].split('/')[-1] if topics else 'Sin categoría'

                # Obtener la foto de perfil del canal (miniatura)
                thumbnails = channel_details.get('snippet', {}).get('thumbnails', {})
                thumbnail_url = None
                # Preferir 'default', luego 'medium', luego 'high'
                for key in ['default', 'medium', 'high']:
                    if key in thumbnails:
                        thumbnail_url = thumbnails[key]['url']
                        break

                subscriptions.append({
                    'title': item['snippet']['title'],
                    'channel_id': channel_id,
                    'topic': primary_topic,
                    'thumbnail_url': thumbnail_url
                })

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return subscriptions


def calculate_topic_distribution(subscriptions):
    """
    Calcula la frecuencia de cada categoría de suscripción.
    """
    topic_counts = defaultdict(int)
    for sub in subscriptions:
        topic_counts[sub['topic']] += 1
    return dict(topic_counts)
