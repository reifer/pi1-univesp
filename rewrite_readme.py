import codecs

content = """# Bazar Solidário - Documentação Técnica e Onboarding

Este documento reflete a estrutura técnica exata do projeto de doações, detalhando as regras de negócios, tecnologias implementadas e infraestrutura, garantindo integração rápida para novos desenvolvedores.

## 1. 🛠️ Stack Tecnológica (Backend e Frontend)

### Backend
- **Linguagem:** Python 3.13+
- **Framework Principal:** Django (Servidor configurado para WSGI via Gunicorn em produção)
- **Gerenciamento de Configuração:** `python-dotenv` para isolamento de credenciais e travas de segurança.
- **ORM e Banco de Dados (Persistência de Dados):**
  - **Produção/Homologação:** PostgreSQL (via adaptador `psycopg2-binary`).
  - **Desenvolvimento Rápido:** SQLite3 (adaptado via flag `DB_ENGINE` no `.env`).

### Frontend (Arquitetura Atual)
- **Estruturação:** Server-Side Rendering via **Django Templates** (extensões `.html`).
- **Estilização:** Tailwind CSS injetado de forma estática via *CDN*.
- **Linguagem Nativa e Comportamento:** JavaScript Vanilla (manipulação de DOM, listeners de eventos `input/change/blur` e requisições HTTP assíncronas via `fetch`).

---

## 2. ⚙️ Funcionalidades, Regras de Negócio e UX

A plataforma foi construída sob rigoroso controle transacional e experiência do usuário:

### Validação de Formulários e UX Dinâmica
- **Busca Assíncrona de CEP (ViaCEP):** Ao preencher 8 dígitos no campo `inputCepRetirada`, o sistema desabilita os sub-campos de endereço, inicia um estado de "loading", pesquisa na API ViaCEP remotamente e trata retornos de erro (`data.erro`) ou limpezas dinâmicas se o usuário apagar o input (`clearAddressFields()`).
- **Condicionais Dinâmicas (Toggles de UI):** A interface ativa/desativa requerimentos e exibições dependendo de escolhas do usuário (Ex: esconder campos de endereço quando marcado "ENTREGA" e exibi-los sob "RETIRADA").
- **Tratativas de Data e Horário:** A interface impede visualmente seleção de datas defasadas e domingos, gerenciando arrays de feedback.

### Regras de Domínio e Persistência (Backend)
- **Sanitização de PII (RegEx):** O método `clean_telefone` no `bazar/forms.py` limpa todos os caracteres não numéricos (`\\D`) via expressões regulares, garantindo que o banco armazene apenas o formato telefônico bruto para evitar injeções.
- **Modelos Condicionais e Proteção a Nível de Banco de Dados:** O cadastro valida ativamente o preenchimento de *Logradouro*, *Bairro* e *UF* na View e no Form **se, e somente se**, a modalidade for "RETIRADA". 
- **Integridade Estrutural:** Uma constraint explícita (`CheckConstraint`) no model `Doacao` barra corrupção de dados garantindo que campos de retirada jamais entrem em brancos na tabela.

---

## 3. 🔒 Arquitetura de Segurança (Hardening) e Autorização

- **Travas Estruturais contra Vazamentos:** O sistema intercepta configurações frouxas em `core/settings.py` e interrompe o boot se a `SECRET_KEY` tiver menos de 50 caracteres (ou for originária do framework, contendo `django-insecure-`). Também bloqueia inicializações com host curinga (`*`) se a flag de debug for nativa de produção (`DEBUG=False`).
- **Prevenção de IDOR e Roles:** Views sensíveis de administração/detalhamento (como `doacao_detalhe`) são estritamente isoladas pelo decorator `@user_passes_test(lambda u: u.is_staff)`, desabilitando chutes de ID no painel.
- **Blindagem de Transmissão (Production Ready):** Em modo de compilação de produção, o sistema ativa forçadamente o tráfego restrito: Cookie Secure (`SESSION_COOKIE_SECURE` / `CSRF_COOKIE_SECURE`), redirecionamento de SSL (`SECURE_SSL_REDIRECT`), bloqueadores NOSNIFF, e o HSTS de 1 ano de preload.

---

## 4. 🏗️ Infraestrutura e Fluxos de Deploy

- **Conteinerização (Agnóstica a CI/CD):** Não há pipelines evidentes em `.github/workflows` ou similares; o projeto orbita ao redor da infra de **contêineres locais**. Um `Dockerfile` empacota a aplicação isolando o interpretador, enquanto um `docker-compose.yml` rege o sincronismo com o serviço de banco de dados nativo do host.
- **Hierarquia Visual de Ambientes:**
  - **Dev/Local:** Execução acorrentada com `.env.example` preenchido base, subindo o `sqlite` nativo com `DEBUG=True`.
  - **Homologação/Produção:** Foco na transição pro `gunicorn`, conectando-se ao container `db` (Postgres).

---

## 5. 🚦 Setup e Guia de Ambientes

### Opção A: Setup com Docker (Mimetizando Produção/DB Externo)
1. Suba os containers do ecossistema:
   ```bash
   docker compose up --build
   ```
2. Migre o banco e popule um superusuário no container web:
   ```bash
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   ```

### Opção B: Setup Local (SQLite3 Dinâmico)
1. Configure as chaves base (`.env`):
   ```dotenv
   DB_ENGINE=sqlite
   SQLITE_NAME=db.sqlite3
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```
2. Ative sua Virtual Environment vindo do repositório, baixe o ecossistema e ligue:
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

A porta padronizada do projeto servirá a requisição em `http://127.0.0.1:8000`.
"""

with codecs.open('README.md', 'w', encoding='utf-8') as f:
    f.write(content)
