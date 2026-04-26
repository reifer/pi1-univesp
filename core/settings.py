import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis do seu arquivo .env que já existe na raiz
load_dotenv()

WHATSAPP_NUMERO = os.getenv('WHATSAPP_NUMERO', '').strip()
WHATSAPP_MENSAGEM_PADRAO = os.getenv('WHATSAPP_MENSAGEM_PADRAO', '').strip()


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 't', 'yes', 'y', 'on')

BASE_DIR = Path(__file__).resolve().parent.parent

from django.core.exceptions import ImproperlyConfigured

def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = f"ImproperlyConfigured: Set the {var_name} environment variable"
        raise ImproperlyConfigured(error_msg)

# Chave de segurança
SECRET_KEY = get_env_variable('SECRET_KEY')

if len(SECRET_KEY) < 50 or 'django-insecure-' in SECRET_KEY:
    raise ImproperlyConfigured("A SECRET_KEY deve ter pelo menos 50 caracteres e não conter 'django-insecure-'.")

DEBUG = env_bool('DEBUG', False)

ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '').split(',') if host.strip()]

if not DEBUG and '*' in ALLOWED_HOSTS:
    raise ImproperlyConfigured("ALLOWED_HOSTS não deve aceitar '*' quando o DEBUG estiver desligado (em produção).")

# Lista de aplicativos instalados
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bazar', # O seu aplicativo do Bazar Solidário
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Alterado para incluir a pasta raiz de templates e a pasta do app bazar
        'DIRS': [
            os.path.join(BASE_DIR, 'bazar', 'templates'),
            os.path.join(BASE_DIR, 'bazar', 'templates', 'registration'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'bazar.context_processors.whatsapp_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Configuração do banco por ambiente (PostgreSQL ou SQLite)
db_engine = os.getenv('DB_ENGINE', 'postgresql').strip().lower()
running_tests = len(sys.argv) > 1 and sys.argv[1] == 'test'

if running_tests:
    db_engine = 'sqlite'

if db_engine == 'sqlite':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, os.getenv('SQLITE_NAME', 'db.sqlite3')),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': get_env_variable('DB_NAME'),
            'USER': get_env_variable('DB_USER'),
            'PASSWORD': get_env_variable('DB_PASS'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }

# Configurações de Internacionalização
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Arquivos Estáticos (CSS, Imagens)
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'bazar', 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # Adicionado para melhor gestão de estáticos

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CONFIGURAÇÕES DE SEGURANÇA (PRODUÇÃO E DESENVOLVIMENTO) ---
if not DEBUG:
    # --- Produção Blindada ---
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 ano
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    # --- Ambiente Local ---
    SECURE_BROWSER_XSS_FILTER = False
    SECURE_CONTENT_TYPE_NOSNIFF = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False

# --- CONFIGURAÇÕES DE AUTENTICAÇÃO ---
LOGIN_REDIRECT_URL = 'admin_dashboard'
LOGOUT_REDIRECT_URL = 'index'
LOGIN_URL = 'login'

TEST_RUNNER = 'bazar.test_runner.ExecutorDeTestesAuditoria'