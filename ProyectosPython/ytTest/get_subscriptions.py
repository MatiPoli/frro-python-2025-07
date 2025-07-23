import os
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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


def list_my_subscriptions(youtube_service):
    subscriptions = []
    next_page_token = None

    while True:
        request = youtube_service.subscriptions().list(
            part='snippet',
            mine=True,
            maxResults=50,  # Puedes obtener hasta 50 suscripciones por solicitud
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            subscriptions.append(item['snippet']['title'])

        next_page_token = response.get('nextPageToken')

        if not next_page_token:
            break

    return subscriptions

def list_my_topics(youtube_service):
    topics = []

    request = youtube_service.channels().list(
        part="topicDetails",
        id="UCvoWO5mqlH90KJXTTB-Ktdg", #ID del canal. Se puede obtener desde la pagina del canal -> mas -> compartir canal -> copiar id del canal
    )
    response = request.execute()

    print(response)

    return topics

if __name__ == '__main__':
    try:
        youtube = get_authenticated_service()
        print("Autenticación exitosa. Obteniendo tus suscripciones...")

        my_subscriptions = list_my_topics(youtube)

        print(f"Tienes {len(my_subscriptions)} suscripciones:")
        for sub in sorted(my_subscriptions):  # Para verlas ordenadas alfabéticamente
            print(f"- {sub}")

    except HttpError as e:
        print(f"Ocurrió un error HTTP {e.resp.status}: {e.content}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")