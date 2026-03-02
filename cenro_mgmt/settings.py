import os
from pathlib import Path
import dj_database_url
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------
# Core config
# -------------------------
SECRET_KEY = config("SECRET_KEY", default="replace-me-in-production")

def _debug():
    try:
        return config("DEBUG", default="False", cast=bool)
    except Exception:
        return False

DEBUG = _debug()

# Hostnames only (NO https://). Comma-separated on Render.
# Default allows localhost and any *.onrender.com host, so new services
# like cenro-management-dzeg.onrender.com work even if ALLOWED_HOSTS
# is not explicitly set yet.
try:
    ALLOWED_HOSTS = config(
        "ALLOWED_HOSTS",
        default="localhost,127.0.0.1,.onrender.com",
        cast=Csv(),
    )
except Exception:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", ".onrender.com"]

# Full origins WITH https://. Comma-separated on Render.
# Django supports wildcard CSRF origins like https://*.onrender.com
try:
    _csv_origins = config(
        "CSRF_TRUSTED_ORIGINS",
        default="https://*.onrender.com",
    )
except Exception:
    _csv_origins = "https://*.onrender.com"

CSRF_TRUSTED_ORIGINS = [s.strip() for s in _csv_origins.split(",") if s.strip()]


# Recommended when behind Render/Cloudflare proxy (helps Django know request is HTTPS)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# -------------------------
# Apps
# -------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Project apps
    "accounts",
    "services",
    "scheduling",
    "dashboard",
]


# -------------------------
# Middleware
# -------------------------
MIDDLEWARE = [
    # Must be first to log unhandled exceptions
    "cenro_mgmt.middleware.ExceptionLoggingMiddleware",

    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "cenro_mgmt.middleware.LoginRequiredMiddleware",
]


ROOT_URLCONF = "cenro_mgmt.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "cenro_mgmt.wsgi.application"


# -------------------------
# Database
# -------------------------
def _get_database_config():
    """
    Use DATABASE_URL if set (Render Postgres); otherwise SQLite for local dev.
    """
    try:
        database_url = config("DATABASE_URL", default=None)
    except Exception:
        database_url = None

    if database_url:
        try:
            # conn_max_age improves performance on Render
            return dj_database_url.parse(database_url, conn_max_age=600)
        except Exception:
            pass

    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }

DATABASES = {"default": _get_database_config()}


# -------------------------
# Auth
# -------------------------
AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "dashboard:home"


# -------------------------
# i18n
# -------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Manila"
USE_I18N = True
USE_TZ = True


# -------------------------
# Static & Media
# -------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Avoid manifest-related 500s (safer while debugging)
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}


# -------------------------
# Security cookies (NOW actually uses your env vars)
# -------------------------
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=False, cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=False, cast=bool)


# -------------------------
# Default auto field
# -------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# -------------------------
# Logging (Render-friendly)
# -------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "verbose_tb": {
            "format": "{levelname} {asctime} {module}\n{message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "verbose",
        },
        "console_tb": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "verbose_tb",
        },
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django.request": {
            "handlers": ["console_tb"],
            "level": "ERROR",
            "propagate": False,
        },
        "accounts": {
            "handlers": ["console_tb"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}