# Bazar Solidario - Guia de Onboarding

Este documento foi atualizado para permitir que qualquer integrante suba o projeto rapidamente com um fluxo padrao e previsivel.

## 1. Visao Geral

Stack principal:
- Python 3.13+
- Django
- PostgreSQL (homologacao/producao)
- SQLite (desenvolvimento rapido opcional)
- Tailwind via CDN (frontend)

Aplicacao principal:
- App: bazar
- Configuracao central: core/settings.py

## 2. Pre-Requisitos

Para qualquer opcao:
- Git
- Python 3.13+ (se for rodar sem Docker)
- Docker Desktop + Docker Compose (se for rodar com Docker)

## 3. Variaveis de Ambiente (.env)

Copie o arquivo de exemplo e ajuste os valores:

```bash
cp .env.example .env
```

No Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

### Variaveis obrigatorias

- SECRET_KEY: chave criptografica do Django. Nunca usar chave de desenvolvimento em producao.
- DEBUG: habilita/desabilita modo debug. Em producao deve ser False.
- ALLOWED_HOSTS: lista de hosts permitidos, separada por virgula.
- SECURE_BROWSER_XSS_FILTER: hardening basico contra XSS no navegador.
- SECURE_CONTENT_TYPE_NOSNIFF: evita MIME sniffing.
- SESSION_COOKIE_SECURE: cookie de sessao apenas via HTTPS quando True.
- CSRF_COOKIE_SECURE: cookie CSRF apenas via HTTPS quando True.

### Variaveis de banco

Modo PostgreSQL:
- DB_ENGINE=postgresql
- DB_NAME
- DB_USER
- DB_PASS
- DB_HOST
- DB_PORT

Modo SQLite (desenvolvimento rapido):
- DB_ENGINE=sqlite
- SQLITE_NAME=db.sqlite3

Observacao:
- O projeto suporta escolha de banco por DB_ENGINE no core/settings.py.

## 4. Como Rodar o Projeto

## Opcao A: Docker (recomendado para homologacao/producao)

Esta opcao sobe aplicacao + PostgreSQL com ambiente padronizado.

1. Suba os containers:

```bash
docker compose up --build
```

2. Em outro terminal, aplique migracoes:

```bash
docker compose exec web python manage.py migrate
```

3. Crie superusuario:

```bash
docker compose exec web python manage.py createsuperuser
```

4. Acesse:
- App: http://127.0.0.1:8000
- Admin: http://127.0.0.1:8000/admin

Como a configuracao funciona:
- O servico db (PostgreSQL) e criado pelo docker-compose.yml.
- O servico web recebe variaveis de ambiente via .env e overrides internos para conectar no host db.
- Nao e necessario instalar PostgreSQL local nessa opcao.

## Opcao B: Local com SQLite (desenvolvimento rapido)

Ideal para testar features sem dependencias de banco externo.

1. Defina no .env:

```dotenv
DB_ENGINE=sqlite
SQLITE_NAME=db.sqlite3
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

2. Crie e ative o ambiente virtual:

Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instale dependencias:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. Rode migracoes:

```bash
python manage.py migrate
```

5. Crie superusuario:

```bash
python manage.py createsuperuser
```

6. Inicie o servidor:

```bash
python manage.py runserver
```

7. Acesse:
- App: http://127.0.0.1:8000
- Admin: http://127.0.0.1:8000/admin

## 5. Comandos Operacionais

Executar testes:

```bash
python manage.py test
```

Checar consistencia de migracoes:

```bash
python manage.py makemigrations --check --dry-run
```

Gerar novas migracoes (quando houver alteracao de model):

```bash
python manage.py makemigrations
python manage.py migrate
```

## 6. Notas de Qualidade e Seguranca

Estado atual apos refatoracao:
- Protecao de dados sensiveis em telas publicas (LGPD).
- Fluxo transacional de cadastro com rollback em falha.
- Validacao de endereco para retirada.
- Suite de testes automatizados cobrindo privacidade, atomicidade, validacao e fluxo completo.

Recomendacoes para equipe:
- Sempre rodar python manage.py test antes de push.
- Evitar alterar rules de acesso sem teste de regressao.
- Em producao, usar DEBUG=False e cookies secure=True com HTTPS.

## 7. Estrutura de Arquivos Relevantes

- core/settings.py: configuracao de ambiente, seguranca e banco.
- core/urls.py: rotas globais e autenticacao.
- bazar/models.py: schema principal (Doador, Doacao, Agendamento).
- bazar/views.py: fluxo de cadastro, privacidade e operacoes administrativas.
- bazar/forms.py: validacao de entrada via ModelForm.
- bazar/tests.py: testes automatizados de regressao.
- docker-compose.yml: orquestracao local com PostgreSQL.
- Dockerfile: imagem da aplicacao Django.

## 8. Troubleshooting Rapido

Erro de modulo Django:
- Verifique se o ambiente virtual esta ativo.

Erro de conexao no PostgreSQL com Docker:
- Verifique se o servico db esta healthy:

```bash
docker compose ps
```

Migracoes fora de sincronia:

```bash
python manage.py makemigrations --check --dry-run
```

Se voce seguir uma das opcoes acima, o projeto deve subir em menos de 10 minutos.
