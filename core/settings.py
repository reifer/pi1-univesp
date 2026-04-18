import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis do seu arquivo .env que já existe na raiz
load_dotenv()


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 't', 'yes', 'y', 'on')

BASE_DIR = Path(__file__).resolve().parent.parent

# Chave de segurança
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me')

DEBUG = env_bool('DEBUG', False)

ALLOWED_HOSTS = [host.strip() for host in os.getenv('ALLOWED_HOSTS', '').split(',') if host.strip()]

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
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Configuração do Banco de Dados PostgreSQL (usando seu .env)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'pi_univesp'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASS', 'admin'),
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

# --- CONFIGURAÇÕES DE SEGURANÇA (PRODUÇÃO) ---
SECURE_BROWSER_XSS_FILTER = env_bool('SECURE_BROWSER_XSS_FILTER', True)
SECURE_CONTENT_TYPE_NOSNIFF = env_bool('SECURE_CONTENT_TYPE_NOSNIFF', True)
SESSION_COOKIE_SECURE = env_bool('SESSION_COOKIE_SECURE', not DEBUG)
CSRF_COOKIE_SECURE = env_bool('CSRF_COOKIE_SECURE', not DEBUG)

# --- CONFIGURAÇÕES DE AUTENTICAÇÃO ---
LOGIN_REDIRECT_URL = 'admin_dashboard'
LOGOUT_REDIRECT_URL = 'index'
LOGIN_URL = 'login'