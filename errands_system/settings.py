import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = int(os.environ.get("DEBUG", default=0))

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
    # 'debug_toolbar',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'djoser',
    'django_ical',
    'drf_yasg',
    'rest_registration',
    'changelog.apps.ChangelogConfig',
    'errands.apps.ErrandsConfig',
    'django_cleanup.apps.CleanupConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'changelog.middleware.LoggedInUserMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
]

ROOT_URLCONF = 'errands_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'errands_system.wsgi.application'

DATABASES = {
    'default': {
        "ENGINE": os.environ.get("SQL_ENGINE"),
        "NAME": os.environ.get("SQL_DATABASE"),
        "USER": os.environ.get("SQL_USER"),
        "PASSWORD": os.environ.get("SQL_PASSWORD"),
        "HOST": os.environ.get("SQL_HOST"),
        "PORT": os.environ.get("SQL_PORT"),
    }
}
AUTH_USER_MODEL = 'users.CustomUser'
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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'users.authentication.ExpiringTokenAuthentication',
    ),
}
TOKEN_EXPIRED_AFTER_SECONDS = 604800

DJOSER = {
    'PASSWORD_RESET_CONFIRM_URL': 'reset/{uid}/{token}/',
    'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': True,
}
SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False
}
LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = Path.joinpath(BASE_DIR, "static")
STATIC_DIR = Path.joinpath(BASE_DIR, "static")
# STATICFILES_DIRS = (STATIC_ROOT,)
MEDIA_URL = 'https://back-missions.admlr.lipetsk.ru/media/'
MEDIA_ROOT = Path.joinpath(BASE_DIR, "media")

CORS_ORIGIN_ALLOW_ALL = True

FILE_UPLOAD_PERMISSIONS = 0o757
# INTERNAL_IPS = ['localhost', 'back-missions.admlr.lipetsk.ru']
# DEBUG_TOOLBAR_CONFIG = {
#     "SHOW_TOOLBAR_CALLBACK": lambda request: True,
# }
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'obu.its@yandex.ru'
EMAIL_HOST_PASSWORD = 'OBUITC48'
DEFAULT_FROM_EMAIL = 'obu.its@yandex.ru'

REST_REGISTRATION = {
    'REGISTER_VERIFICATION_ENABLED': False,
    'SEND_RESET_PASSWORD_LINK_SERIALIZER_USE_EMAIL': True,
    'RESET_PASSWORD_VERIFICATION_ENABLED': True,
    'RESET_PASSWORD_VERIFICATION_URL': 'https://todo.admlr.lipetsk.ru/auth/password_restore',
    'REGISTER_EMAIL_VERIFICATION_ENABLED': False,
    'RESET_PASSWORD_VERIFICATION_EMAIL_TEMPLATES': {'body': 'reset_password/body.txt',
                                                    'subject': 'reset_password/subject.txt'},
    'VERIFICATION_FROM_EMAIL': 'obu.its@yandex.ru',
}
