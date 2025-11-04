"""
Django settings for horunap_api project.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-%ava0+yal+003l5u#byx4n$fi)k)^wf7vmlmdur*9db3e10=c)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# --- CONFIGURACIÓN CRÍTICA: User personalizado ---
AUTH_USER_MODEL = 'users.User'


# --- Application definition ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions', # Necesario para las sesiones
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # --- Apps de terceros (API y CORS) ---
    'rest_framework',
    'corsheaders',

    # --- Apps Locales ---
    'users',
    'academic',
    'schedule',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware', # Necesario para las sesiones
    'corsheaders.middleware.CorsMiddleware', # Debe ir antes de CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'horunap_api.middleware.RedireccionAutenticacionMiddleware', # Comentado para probar el login
]

ROOT_URLCONF = 'horunap_api.urls'

# --- Configuración de Templates ---
# (Asegúrate de tener solo UNA definición de TEMPLATES)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')], # Directorio general de templates
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

WSGI_APPLICATION = 'horunap_api.wsgi.application'


# --- Database ---
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- CAMBIAR CÓMO SE GUARDAN LAS SESIONES (PRUEBA) ---
SESSION_ENGINE = 'django.contrib.sessions.backends.file'
# SESSION_ENGINE = 'django.contrib.sessions.backends.db' # Opción por defecto


# --- Password validation ---
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# --- Configuración de archivos estáticos (CSS, JS, imágenes) ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'), # Directorio general de archivos estáticos
]

# --- Configuración de autenticación y redirección ---
LOGIN_URL = '/login/' # URL de tu vista de login
LOGIN_REDIRECT_URL = '/users/' # URL a la que redirigir DESPUÉS del login (tu vista de redirección por rol)
LOGOUT_REDIRECT_URL = '/login/' # URL a la que redirigir DESPUÉS del logout

# --- Internationalization ---
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-es' # o 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_L10N = True # Para formatos de fecha/número locales
USE_TZ = True # Recomendado para manejar zonas horarias

DEFAULT_CHARSET = 'utf-8'

# --- Default primary key field type ---
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Configuración de CORS ---
# Orígenes (dominios) que tienen permiso para hacer peticiones a esta API
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # Puerto estándar de React en desarrollo
    'http://127.0.0.1:3000',
]
# Si necesitas permitir credenciales (cookies, etc.) desde React (útil para login con sesiones)
# CORS_ALLOW_CREDENTIALS = True

# Opcional: Para desarrollo, puedes permitir todos los orígenes (NO USAR EN PRODUCCIÓN)
# CORS_ALLOW_ALL_ORIGINS = True

AUTHENTICATION_BACKENDS = ['users.backends.DebugModelBackend']