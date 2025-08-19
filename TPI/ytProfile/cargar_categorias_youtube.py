import os
import django
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Friendscriptions.settings')
django.setup()

from ytProfile.models import Categoria

# Configuración de la API de YouTube
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
CLIENT_SECRETS_FILE = 'client_secret.json'  # Debe estar en la raíz del proyecto

# Autenticación y construcción del servicio
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    CLIENT_SECRETS_FILE, SCOPES)
credentials = flow.run_console()
youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

try:
    # Obtener todas las categorías de video
    response = youtube.videoCategories().list(
        part='snippet',
        regionCode='AR'  # Cambia el país si lo deseas
    ).execute()

    for item in response.get('items', []):
        if item['snippet'].get('assignable', False):
            cat_id = item['id']
            title = item['snippet']['title']
            obj, created = Categoria.objects.get_or_create(id=cat_id, defaults={'tematica': title})
            print(f"{'Creada' if created else 'Ya existe'}: {title} (id={cat_id})")
except HttpError as e:
    print(f"Error al obtener categorías: {e}")
