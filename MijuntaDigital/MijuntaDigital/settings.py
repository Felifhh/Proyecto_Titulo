from pathlib import Path
import os
from django.urls import reverse_lazy

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
SECRET_KEY = 'django-insecure-lvagyi3pl#txvtb5!h2$!ldgkxl4821=txet-^%=pt2l%x6&vz'
DEBUG = True
ALLOWED_HOSTS = []

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
            ],
        },
    },
]

WSGI_APPLICATION = 'MijuntaDigital.wsgi.application'

# =========================================
# BASE DE DATOS
# =========================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'junta_vecinal',
        'USER': 'django_user',
        'PASSWORD': 'junta123',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

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