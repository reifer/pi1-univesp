# 🎁 Bazar Solidário - Conexão Solidária

**Sistema Web para Gerenciamento de Doações e Logística de Coleta**

Um projeto Django moderno, responsivo e intuitivo para facilitar doações beneficentes com agendamento automático de retirada, integração com ViaCEP e painel administrativo robusto.

---

## 📋 Pré-requisitos

Antes de começar, certifique-se de que seu computador possui:

- **Python 3.10+** (recomendado 3.13+)
  - [Download Python](https://www.python.org/downloads/)
  - Verifique a instalação: `python --version`

- **Git** (para clonar o repositório)
  - [Download Git](https://git-scm.com/)
  - Verifique a instalação: `git --version`

- **Conexão com Internet** ⚠️
  - Obrigatório para carregar: Tailwind CSS (CDN), ViaCEP API, Google Maps API
  - Se offline, algumas funcionalidades podem não funcionar

---

## 🚀 Passo a Passo de Instalação

### 1️⃣ Clone o Repositório

```bash
git clone -b master https://github.com/reifer/pi1-univesp.git
cd PI_Univesp
```

**Nota:** Use `-b master` para a branch mais estável (produção). Use `-b dev` para a branch de desenvolvimento.

---

### 2️⃣ Crie e Ative o Ambiente Virtual

#### **Windows (PowerShell)**

```powershell
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
.\venv\Scripts\Activate.ps1
```

#### **Linux/Mac (Bash/Zsh)**

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate
```

Após ativar, seu terminal deve mostrar o prefixo `(venv)`.

---

### 3️⃣ Instale as Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Este comando instala todas as bibliotecas necessárias (Django, Pillow, etc).

---

## 🗄️ Configuração do Banco de Dados

### 1️⃣ Execute as Migrações

```bash
python manage.py migrate
```

Este comando cria as tabelas no banco de dados SQLite local (`db.sqlite3`).

---

### 2️⃣ Crie um Usuário Administrador

```bash
python manage.py createsuperuser
```

Siga os prompts:

```
Username: admin
Email: seu@email.com
Password: ••••••••
Password (again): ••••••••
```

**💡 Dica:** Use credenciais simples para desenvolvimento (ex: admin / 123456).

---

## ▶️ Execução do Projeto

### Inicie o Servidor de Desenvolvimento

```bash
python manage.py runserver
```

**Saída esperada:**

```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

### 🌐 Acesse a Aplicação

Abra seu navegador e acesse:

- **Homepage:** http://127.0.0.1:8000/
- **Painel Admin:** http://127.0.0.1:8000/admin/
  - Use as credenciais criadas no `createsuperuser`

---

## 📁 Estrutura de Pastas

```
PI_Univesp/
├── bazar/                          # App principal
│   ├── migrations/                 # Histórico de alterações do banco
│   ├── static/                     # Arquivos CSS, JS, imagens
│   │   ├── css/
│   │   └── images/
│   ├── templates/                  # Templates HTML
│   │   ├── bazar/                  # Templates da app
│   │   └── registration/           # Templates de login
│   ├── models.py                   # Modelos de dados (Doacao, Doador, Agendamento)
│   ├── views.py                    # Lógica das rotas (controllers)
│   ├── urls.py                     # Definição de rotas
│   ├── admin.py                    # Configuração do painel admin
│   └── apps.py                     # Configuração da app
│
├── core/                           # Configurações do Django
│   ├── settings.py                 # Variáveis de ambiente, apps, databases
│   ├── urls.py                     # Rotas globais
│   └── wsgi.py                     # Configuração para deploy
│
├── docs/                           # Documentação adicional
│   └── CONTRATO_BACKEND_FRONTEND.md
│
├── manage.py                       # Gerenciador do Django
├── requirements.txt                # Dependências do projeto
├── db.sqlite3                      # Banco de dados (gerado após migrate)
└── README.md                       # Este arquivo
```

**Explicação:**

- **`bazar/`**: Aplikação Django principal. Contém toda a lógica de negócio (modelos, visualizações, templates).
- **`core/`**: Configurações gerais do Django (settings, URLs raiz, WSGI).
- **`docs/`**: Documentação técnica interna e contratos frontend-backend.

---

## ✨ Funcionalidades Implementadas

### 🎯 Gerenciamento de Doações

- ✅ Formulário público de cadastro de doações
- ✅ Campos: Nome item, Categoria, Tamanho, Descrição, Quantidade
- ✅ Categorias com checkboxes: Roupa, Calçados, Acessórios, Brinquedos, Outros
- ✅ Validação de email e telefone (com máscara inteligente)

### 📍 Integração ViaCEP

- ✅ Auto-preenchimento de endereço via CEP
- ✅ Busca em tempo real com máscara (00000-000)
- ✅ Campos: Logradouro, Número, Complemento, Bairro, Cidade, UF
- ✅ Validação automática de CEP

### 📅 Agendamento Inteligente

- ✅ **Retirada:** Segundas e Quartas (09:00 - 17:00)
- ✅ **Entrega:** Terças, Quintas e Domingos
- ✅ Validação de datas passadas
- ✅ Feedback visual em tempo real

### 🗺️ Integração Google Maps

- ✅ Links diretos para rota no Google Maps
- ✅ Query com endereço completo (rua, número, bairro, CEP)
- ✅ Disponível apenas em telas desktop (hidden em mobile)

### 👨‍💼 Painel Administrativo

- ✅ Dashboard com duas abas: **Logística** e **Estoque**
- ✅ Tabela de Retirada: Doador, Data, Horário, Endereço
- ✅ Tabela de Entrega: Doador, Data Prevista, Status
- ✅ Filtro de inventário por nome/categoria/tamanho
- ✅ Contador de itens disponíveis em estoque
- ✅ Ações: Marcar como Coletado, Marcar como Recebido, Dar Baixa, Excluir

### 🔐 Segurança

- ✅ Autenticação Django nativa
- ✅ Toggle "Ver Senha" no formulário de login
- ✅ Proteção contra CSRF (token Django)
- ✅ Restrição de painel admin apenas para staff

### 📱 Responsividade

- ✅ Mobile-first design com Tailwind CSS
- ✅ Grid adaptativo (2 colunas mobile → 3 desktop)
- ✅ Botões e links otimizados para touch
- ✅ Tabelas com scroll horizontal em mobile

---

## 🔧 Comandos Úteis

### Criar Migrações (após modificar models.py)

```bash
python manage.py makemigrations
python manage.py migrate
```

### Acessar o Shell do Django

```bash
python manage.py shell
```

Útil para testes rápidos:

```python
from bazar.models import Doacao, Doador
doadores = Doador.objects.all()
doacoes = Doacao.objects.filter(status='PENDENTE')
```

### Coletador de Arquivos Estáticos (para deploy)

```bash
python manage.py collectstatic --noinput
```

### Limpar Cache do Banco

```bash
python manage.py flush
# ⚠️ Cuidado! Deleta todos os dados
```

---

## ⚠️ Avisos Importantes

### 🌐 Conexão com Internet (Obrigatório)

O projeto depende de recursos externos via CDN e APIs:

| Recurso | Origem | Uso |
|---------|--------|-----|
| **Tailwind CSS** | CDN jsDelivr | Estilização de componentes |
| **ViaCEP API** | viacep.com.br | Auto-preenchimento de endereços |
| **Google Maps** | google.com/maps | Links de navegação logística |
| **Ícones SVG** | Embutidos | UI (inclusos no projeto) |

**Se sem internet:** Formulários funcionarão, mas ViaCEP e Google Maps não funcionarão.

---

### 🗄️ Banco de Dados Local

O projeto usa **SQLite** por padrão (ideal para desenvolvimento).

- Arquivo: `db.sqlite3`
- **Não** adicione ao Git (já está em `.gitignore`)
- Para reset: Delete `db.sqlite3` e rode `python manage.py migrate`

---

### 🔑 Senha Padrão do Admin

Nunca configure a mesma senha em produção! Use variáveis de ambiente.

---

## 🚨 Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'django'"

**Solução:** A venv não está ativada.

```bash
# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

---

### ❌ "Connection refused" ao acessar o servidor

**Solução:** Verifique se o servidor está rodando.

```bash
python manage.py runserver 0.0.0.0:8000  # Exponha em todas as interfaces
```

---

### ❌ "No such table: bazar_doacao"

**Solução:** As migrações não foram aplicadas.

```bash
python manage.py migrate
```

---

### ❌ ViaCEP/"Google Maps não funcionam

**Solução:** Verifique conexão com internet.

```bash
# Teste a conexão
ping viacep.com.br
curl https://viacep.com.br/ws/01310100/json/
```

---

## 📚 Documentação Adicional

- **[Contrato Backend-Frontend](docs/CONTRATO_BACKEND_FRONTEND.md)** - Especificação técnica de rotas e tipos de dados
- **[Django Oficial](https://docs.djangoproject.com/)** - Documentação do framework
- **[Tailwind CSS](https://tailwindcss.com/)** - Guia de classes de estilo

---

## 👥 Contribuição

Para contribuir com melhorias:

1. Crie uma branch: `git checkout -b feature/sua-feature`
2. Commit suas mudanças: `git commit -m "Adiciona feature X"`
3. Faça push: `git push origin feature/sua-feature`
4. Abra um Pull Request

---

## 📝 Licença

Este projeto é desenvolvido como trabalho acadêmico para a **UNIVESP**.

---

## 💬 Dúvidas?

Se encontrar problemas:

1. Verifique este README
2. Confira os logs do servidor (`python manage.py runserver`)
3. Abra uma issue no repositório
4. Contacte o time de desenvolvimento

---

**Última atualização:** 14 de Abril de 2026  
**Versão:** 2.0 (Com Checkboxes de Categoria)  
**Status:** ✅ Em Produção
