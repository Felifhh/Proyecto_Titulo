from pathlib import Path
import os
from django.urls import reverse_lazy
from dotenv import load_dotenv

load_dotenv()
# =========================================
# RUTAS BÁSICAS
# =========================================
BASE_DIR = Path(__file__).resolve().parent.parent

# =========================================
# LOGIN / LOGOUT
# =========================================
LOGIN_URL = reverse_lazy('usuarios_login')
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# =========================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# =========================================
# Archivos estáticos (CSS, JS, imágenes del sitio)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # opcional para deploy

# Archivos subidos por usuarios (fotos, evidencias)
MEDIA_URL = '/user_media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'static', 'media')

# 💡 Nota:
# Usamos '/user_media/' en vez de '/static/media/' para evitar conflictos.
# Los archivos se guardan físicamente en static/media/
# y se acceden desde http://localhost:8000/user_media/archivo.pdf

# =========================================
# SEGURIDAD Y CONFIGURACIÓN BASE
# =========================================
SECRET_KEY = "django-insecure-lvagyi3pl#txvtb5!h2$!ldgkxl4821=txet-^%=pt2l%x6&vz"
DEBUG = True
ALLOWED_HOSTS = []

# =========================================
# Configuracion de Credenciales
# =========================================

# =========================================
# Cargar credenciales de Supabase desde N8N
# =========================================
import requests
import json

def load_supabase_connection():
    """
    Carga SUPABASE_URL y SUPABASE_KEY desde n8n.
    """
    try:
        url = "https://felifhhh.app.n8n.cloud/webhook/get-supabase-credentials"
        response = requests.get(url, timeout=10)


        # AHORA EL JSON YA NO ES LISTA
        data = response.json()

        SUPABASE_URL = data.get("SUPABASE_URL", "").strip()
        SUPABASE_KEY = data.get("SUPABASE_KEY", "").strip()

        print("SUPABASE_URL recibido:", SUPABASE_URL)
        print("SUPABASE_KEY recibido:", SUPABASE_KEY[:15] + "...")



        if not SUPABASE_URL or not SUPABASE_KEY:
            raise Exception("Credenciales incompletas recibidas desde N8N.")

        return SUPABASE_URL, SUPABASE_KEY
    
    except Exception as e:
        print("Error cargando credenciales Supabase desde N8N:", e)
        return None, None


SUPABASE_URL, SUPABASE_KEY = load_supabase_connection()


# Crear cliente Supabase
from supabase import create_client
supabase = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("⚠ ERROR: Supabase no pudo inicializarse (credenciales ausentes)")



# =========================================
# Cargar credenciales de Google Vision
# desde archivo privado en Supabase Storage
# =========================================
def get_gcp_credentials():
    """
    Descarga el JSON privado de Google Vision desde Supabase Storage.
    Este archivo debe estar en el bucket privado 'credentials'.
    """
    try:
        if not supabase:
            raise Exception("Supabase no inicializado.")

        response = supabase.storage.from_("credentials").download("gcp-vision.json")
        data = response.decode("utf-8")
        return json.loads(data)

    except Exception as e:
        print("Error cargando credenciales GCP:", e)
        return None

# =========================================
# Cargar conexion de SUPABASE BD Y GEMINI API KEY
# desde archivo privado en Supabase Storage
# =========================================

def load_secret_env():
    """
    Descarga y carga las credenciales desde env-secrets.json en Supabase Storage.
    """
    try:
        if not supabase:
            raise Exception("Supabase no está inicializado.")

        response = supabase.storage.from_("credentials").download("env-secrets.json")

        data = json.loads(response.decode("utf-8"))

        # --- DATABASE ---
        SUPABASE_DB_CONFIG = data.get("SUPABASE", {})

        SECRET_SUPABASE_HOST = SUPABASE_DB_CONFIG.get("HOST")
        SECRET_SUPABASE_PORT = SUPABASE_DB_CONFIG.get("PORT")
        SECRET_SUPABASE_DB = SUPABASE_DB_CONFIG.get("DB")
        SECRET_SUPABASE_USER = SUPABASE_DB_CONFIG.get("USER")
        SECRET_SUPABASE_PASSWORD = SUPABASE_DB_CONFIG.get("PASSWORD")

        # --- API KEYS ---
        SECRET_API_KEYS = data.get("API_KEYS", {})

        SECRET_GEMINI_API_KEY = SECRET_API_KEYS.get("GEMINI_API_KEY")

        return {
            "SUPABASE_HOST": SECRET_SUPABASE_HOST,
            "SUPABASE_PORT": SECRET_SUPABASE_PORT,
            "SUPABASE_DB": SECRET_SUPABASE_DB,
            "SUPABASE_USER": SECRET_SUPABASE_USER,
            "SUPABASE_PASSWORD": SECRET_SUPABASE_PASSWORD,
            "GEMINI_API_KEY": SECRET_GEMINI_API_KEY,
        }

    except Exception as e:
        print("Error cargando archivo env-secrets.json:", e)
        return None


# Cargar credenciales
secret_env = load_secret_env()

if secret_env:
    SECRET_SUPABASE_HOST = secret_env["SUPABASE_HOST"]
    SECRET_SUPABASE_PORT = secret_env["SUPABASE_PORT"]
    SECRET_SUPABASE_DB = secret_env["SUPABASE_DB"]
    SECRET_SUPABASE_USER = secret_env["SUPABASE_USER"]
    SECRET_SUPABASE_PASSWORD = secret_env["SUPABASE_PASSWORD"]
    SECRET_GEMINI_API_KEY = secret_env["GEMINI_API_KEY"]

    print("✔ env-secrets.json cargado correctamente.")
else:
    print("⚠ No se pudo cargar env-secrets.json.")

# =========================================
# APLICACIONES INSTALADAS
# =========================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    

    # Aplicaciones del proyecto
    'MijuntaDigital.apps.MijuntaDigitalConfig',
    'Usuarios',
    'Certificados',
    'Proyecto',
    'Reserva',
    'Actividades',
    'Solicitudes',
    'Noticia',
    'Documentos',
    'Auditoria',
    'pagos',
    'Notificaciones',
    'chatbot',

    # Utilidad
    'widget_tweaks',
]

# =========================================
# MIDDLEWARE
# =========================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# =========================================
# TEMPLATES
# =========================================
ROOT_URLCONF = 'MijuntaDigital.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'Notificaciones.context_processors.notificaciones_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'MijuntaDigital.wsgi.application'

# ==========================
# BASE DE DATOS SUPABASE
# ==========================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': SECRET_SUPABASE_HOST,
        'PORT': SECRET_SUPABASE_PORT,
        'NAME': SECRET_SUPABASE_DB,
        'USER': SECRET_SUPABASE_USER,
        'PASSWORD': SECRET_SUPABASE_PASSWORD,
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}




# ==============================================
# GEMINI API KEY (desde Supabase env-secrets.json)
# ==============================================
GEMINI_API_KEY = SECRET_GEMINI_API_KEY
GEMINI_ENABLED = bool(GEMINI_API_KEY)

print("Gemini Enabled:", GEMINI_ENABLED)
print("Gemini API:", GEMINI_API_KEY[:10] + "...")



# =========================================
# VALIDADORES DE CONTRASEÑA
# =========================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =========================================
# INTERNACIONALIZACIÓN
# =========================================
LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True
DATETIME_FORMAT = "d/m/Y H:i:s"


# =========================================
# ID AUTO
# =========================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
X_FRAME_OPTIONS = 'SAMEORIGIN'


# =========================================
# Webpay Transbank Config (modo test)
# =========================================
WEBPAY_COMMERCE_CODE = "597055555532"  # Código de comercio de prueba
WEBPAY_API_KEY = "579B532A7440BB0C9079DED94D31EA161EB9A1A1F9123A2B1D1F52A6E57A4E97"
WEBPAY_ENVIRONMENT = "TEST"




