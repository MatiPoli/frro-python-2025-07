import logging
from typing import Optional

from allauth.socialaccount.models import SocialApp, SocialToken
from django.conf import settings
from django.contrib.auth.models import User
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

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