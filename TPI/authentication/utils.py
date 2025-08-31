import logging
from typing import Optional

from allauth.socialaccount.models import SocialApp, SocialToken
from django.conf import settings
from django.contrib.auth.models import User
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
from django.db import transaction

from ytProfile.models import Canal, Categoria, Subscription

logger = logging.getLogger(__name__)

def get_youtube_service(user: User) -> Optional[Resource]:
    try:
        social_token = SocialToken.objects.get(account__user=user, account__provider='google')


        app = SocialApp.objects.get(provider='google')

        creds = Credentials(
            token=social_token.token,
            refresh_token=social_token.token_secret,
            token_uri='https://oauth2.googleapis.com/token',
            client_id=app.client_id,
            client_secret=app.secret,
            scopes=settings.SOCIALACCOUNT_PROVIDERS['google']['SCOPE'] 
        )

        youtube_service = build('youtube', 'v3', credentials=creds)
        return youtube_service
    except Exception as e:
        logger.error(f"Un error inesperado ocurrió en get_youtube_service: {e}")
        return None

@transaction.atomic
def load_subscriptions(request):
    user = request.user
    youtube = get_youtube_service(user)
    if not youtube:
        print("No se pudo obtener el servicio de YouTube.")
        return
    
    subscriptions = []
    next_page_token = None

    while True:
        response = youtube.subscriptions().list(
            part="snippet",
            mine=True,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in response.get("items", []):
            canal_info = {
                "id": item["snippet"]["resourceId"]["channelId"],
                "snippet": {
                    "title": item["snippet"]["title"],
                    "thumbnails": item["snippet"]["thumbnails"]
                }
            }
            subscriptions.append(canal_info)

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    idsActuales = set(Subscription.objects.filter(usuario=user).values_list('canal__idCanal', flat=True))
    idsNuevos = set(c['id'] for c in subscriptions)

    idsAEliminar = idsActuales - idsNuevos
    idsAAgregar = idsNuevos - idsActuales

    Subscription.objects.filter(usuario=user, canal__idCanal__in=idsAEliminar).delete()

    for canal_data in subscriptions:
        if canal_data['id'] in idsAAgregar:
            canal, _ = Canal.objects.get_or_create(
                idCanal=canal_data['id'],
                defaults={
                    'nombreCanal': canal_data['snippet']['title'],
                    'thumbnail_url': canal_data['snippet']['thumbnails']['default']['url']
                }
            )

            response = youtube.channels().list(
                part="topicDetails",
                id=canal.idCanal
            ).execute()

            items = response.get("items", [])
            if items:
                topicIds = items[0].get("topicDetails", {}).get("topicIds", [])
                if topicIds:
                    categorias = list(Categoria.objects.filter(idCategoria__in=topicIds))
                    if categorias:
                        canal.categorias.set(categorias)
                        canal.save()

            Subscription.objects.create(usuario=user, canal=canal)

    print("Sincronización de suscripciones completada.")

def load_categories(request):
    user = request.user
    youtube = get_youtube_service(user)

    for canal in Canal.objects.all():
        response = youtube.channels().list(
            part="topicDetails",
            id=canal.idCanal
        ).execute()
        
        items = response.get("items", [])
        if items:
            topicIds = items[0].get("topicDetails", {}).get("topicIds", [])
            if topicIds:
                categorias = list(Categoria.objects.filter(idCategoria__in=topicIds))
                if categorias:
                    canal.categorias.set(categorias)
                    canal.save()

    print("Sincronización de categorías completada.")
