import os
import sys
import django
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- INICIO: Corrección para el ModuleNotFoundError ---
# Añadimos la ruta al directorio raíz del proyecto (TPI) para que Django se encuentre
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_path not in sys.path:
    sys.path.append(project_path)
# --- FIN: Corrección ---

# Configura Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Friendscriptions.settings')
django.setup()

from ytProfile.models import Categoria
# Importamos la función para asignar colores
from authentication.scripts.asignar_colores_categorias import asignar_colores

# Configuración de la API de YouTube
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
# La ruta al client_secret.json ahora es relativa a la raíz del proyecto (TPI)
CLIENT_SECRETS_FILE = os.path.join(project_path, 'client_secret.json')

def cargar_y_asignar_colores():
    # Autenticación y construcción del servicio
    try:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, SCOPES)
        # Usamos run_local_server para el flujo de autenticación en un script local
        credentials = flow.run_local_server()
        youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo 'client_secret.json'. Asegúrate de que esté en la raíz del proyecto (TPI).")
        return
    except Exception as e:
        print(f"Error durante la autenticación o construcción del servicio de YouTube: {e}")
        return

    try:
        # Obtener todas las categorías de video
        response = youtube.videoCategories().list(
            part='snippet',
            regionCode='AR'  # Cambia el país si lo deseas
        ).execute()

        print("--- Cargando categorías de YouTube ---")
        for item in response.get('items', []):
            if item['snippet'].get('assignable', False):
                cat_id = item['id']
                title = item['snippet']['title']
                # Usamos update_or_create para asegurar que la temática se actualice si cambia
                obj, created = Categoria.objects.update_or_create(
                    idCategoria=cat_id, 
                    defaults={'tematica': title}
                )
                if created:
                    print(f"Creada: {title} (id={cat_id})")
                else:
                    print(f"Actualizada: {title} (id={cat_id})")
        print("--- Carga de categorías finalizada ---")

    except HttpError as e:
        print(f"Error al obtener categorías de YouTube: {e}")
        # Continuamos para asignar colores a las categorías que ya tengamos

    # --- Asignar colores a TODAS las categorías en la BD ---
    print("\n--- Asignando colores a las categorías ---")
    try:
        asignar_colores() # Esta función ya imprime su propio mensaje de éxito
    except Exception as e:
        print(f"Ocurrió un error al asignar colores: {e}")

if __name__ == "__main__":
    cargar_y_asignar_colores()
