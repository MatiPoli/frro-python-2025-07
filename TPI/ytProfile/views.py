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


def get_authenticated_service():
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)

    # Esto abrirá una ventana del navegador para que te autentiques
    # y autorices la aplicación.
    credentials = flow.run_local_server(port=0)
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)


def get_youtube_service(request):
    """
    Simula la obtención del objeto de servicio de YouTube a partir de la sesión.
    En una implementación real, este objeto sería creado después de la autenticación.
    """
    credentials_data = request.session.get('credentials')
    if not credentials_data:
        # Redirige al inicio de sesión si no hay credenciales
        return None

    # Reconstruye el objeto de credenciales
    credentials = google_auth_oauthlib.flow.credentials.Credentials(**credentials_data)

    # Construye y devuelve el objeto de servicio de YouTube
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

"""
def profile_view(request):
    return HttpResponse("<h1>Esta es la página de perfil</h1>")
"""

def profile_view(request):
    try:
        youtube = get_authenticated_service()
        print("Autenticación exitosa. Obteniendo tus suscripciones...")
        # Obtiene la lista de suscripciones del usuario y los detalles de los canales
        subscriptions_list = get_subscriptions_with_details(youtube)

        # Calcula la distribución de las suscripciones por categoría
        topic_distribution = calculate_topic_distribution(subscriptions_list)

        # Prepara los datos para el gráfico
        chart_data = json.dumps([
            {'category': k, 'count': v} for k, v in topic_distribution.items()
        ])

        # Datos de ejemplo para seguidores y seguidos (no disponibles en la API de YouTube)
        followers_count = 10
        following_count = 15

        context = {
            'username': 'Nombre de Usuario de Ejemplo', # Reemplazar con el nombre de usuario real
            'followers_count': followers_count,
            'following_count': following_count,
            'subscriptions_count': len(subscriptions_list),
            'subscriptions': subscriptions_list,
            'topic_distribution': chart_data,
        }

        return render(request, 'profile.html', context)

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

                subscriptions.append({
                    'title': item['snippet']['title'],
                    'channel_id': channel_id,
                    'topic': primary_topic
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
