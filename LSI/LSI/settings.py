from datetime import timedelta
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-8!q&lh8fb68+u3ji_a^cq(fq)o4eu65rg9mwd8+p(2r^q4@8kf")
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "accounts",
    "Physician",
    "LabTechnician",
    "Phlebotomist",
    "Nurse",
    "admin.apps.AdminConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "LSI.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "LSI.wsgi.application"

DATABASES = {
    'default': {                                 
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     os.getenv('POSTGRES_DB',       'lis_db'),
        'USER':     os.getenv('POSTGRES_USER',     'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'sql884896'),
        'HOST':     os.getenv('POSTGRES_HOST',     'localhost'),
        'PORT':     os.getenv('POSTGRES_PORT',     '5432'),
    }
}
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "accounts.authentication.CookieJWTAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

JWT_AUTH_COOKIE_ACCESS = "access_token"
JWT_AUTH_COOKIE_REFRESH = "refresh_token"
JWT_COOKIE_SECURE = os.getenv("JWT_COOKIE_SECURE", "False").lower() == "true"
JWT_COOKIE_SAMESITE = os.getenv("JWT_COOKIE_SAMESITE", "Lax")

CORS_ALLOW_ALL_ORIGINS = os.getenv("CORS_ALLOW_ALL_ORIGINS", "True").lower() == "true"
CORS_ALLOW_CREDENTIALS = True
