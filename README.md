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

---

## 🛡️ Guia de Inicialização e Auditoria (Hardening & Produção)

O projeto "Bazar Solidário" passou por um processo rigoroso de Hardening de Segurança e transição para arquitetura de produção via **Gunicorn/WSGI**. Leia isso com atenção antes de mexer no código.

### ⚠️ Travas de Ambiente (`.env`)

- **`SECRET_KEY` Validada no Boot:** A chave secreta agora tem verificação de integridade antes do Django subir. **Se a chave possuir menos de 50 caracteres ou o prefixo padrão `django-insecure-`, a aplicação crasha imediatamente com `ImproperlyConfigured`** e se recusa a expor a porta.
- **Desenvolvimento Local:** Lembre-se de configurar obrigatoriamente `DEBUG=True` no seu `.env` para rodar na sua máquina local, senão o sistema bloqueará acessos sob ausência de SSL. Se `DEBUG=False`, o host curinga (`*`) é estritamente proibido.

### 🔄 Fluxo de Comandos para Revisão de Código (Post-Pull)

Se você acabou de dar um `git pull`, seu ambiente local precisa sincronizar com as novas diretrizes. Execute em ordem:

```bash
# 1. Atualize o ambiente (Necessário para o Gunicorn e novas bibliotecas base)
pip install -r requirements.txt

# 2. Sincronize sua base com as novas constraints de segurança
python manage.py migrate

# 3. Auditoria de Produção (O comando que o revisor DEVE rodar para validar o código)
python manage.py check --deploy
```

### 🔒 Destaques da Seção de Segurança
Liste as melhorias arquiteturais entregues na última fase:
- 🛡️ **Proteção contra IDOR e Segregação**: Uso reforçado de bloqueios nas Views com os decoradores de staff (`@user_passes_test`). Impossível acesso direto ou "chute" de IDs numéricos para visualização do fluxo de doação sem estrita autorização da coordenação.
- 👁️ **Blindagem de PII (Personal Identifiable Information)**: Remoção de URLs auto-montadas de rastreamento (ex: Links embutidos do Google Maps). A visualização do endereço do doador foi substituída pela injeção sob demanda com a **Clipboard API** nativa dos browsers. Os dados não trafegam em histórico.
- 🔐 **Cabeçalhos Autônomos de Segurança**: A arquitetura liga proteções profundas de HSTS (preload de 1 ano), restrição estrita via `SSL Redirect`, e cookies confinados `SECURE` e `HTTPOnly` autonomamente quando detecta o modo de produção.

### 🐳 Execução Exclusiva do Banco via Docker

Se você for rodar tudo local (Opção B abaixo), mas não tiver o banco PostgreSQL instalado na máquina de forma nativa e não quiser usar SQLite, suba o contêiner apenas de banco de dados rodando:

```bash
docker compose up -d db
```

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

---

## 🛠️ Solução de Problemas (Troubleshooting)

### 🔒 O navegador força HTTPS no localhost (Erro `SSL_ERROR_RX_RECORD_TOO_LONG`)

> [!IMPORTANT]
> Isso não é um defeito, é um **comportamento esperado** da segurança robusta que implementamos! Isso ocorre porque o protocolo HSTS foi ativado em algum momento (quando você testou o sistema com `DEBUG=False`). O navegador memoriza que o seu `localhost` só pode ser acessado via fluxo criptografado (`https://`).

Se você voltar o ambiente para Desenvolvimento (`DEBUG=True`) e tentar acessar `http://localhost:8000`, o navegador bloqueará o acesso. Para corrigir esse conflito de cache SSL:

1. **Aba Anônima (Rápido):** Acesse a aplicação por uma janela anônima. O cache HSTS não é persistente nela.
2. **Limpar Transporte de Segurança (Chrome/Edge):** Digite `chrome://net-internals/#hsts` na URL, role até **"Delete domain security policies"**, digite `localhost` e clique em *Delete*.
3. **Limpeza de Cache Geral (Firefox/Safari):** Limpe o histórico recente com foco em "Imagens e Arquivos em Cache" e use a funcionalidade "Esquecer este site" no histórico.

💡 **Dica Proativa de Desenvolvimento:**
Alterne os endereços IP. O navegador trata os domínios de forma separada para o cache de segurança HSTS.
* Se bloqueou em `http://localhost:8000` ➡️ Acesse via `http://127.0.0.1:8000`.

---

Se voce seguir uma das opcoes acima, o projeto deve subir em menos de 10 minutos.
