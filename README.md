# Conexão Solidária (Bazar Solidário)
### Documentação Técnica e Acadêmica do Projeto Integrador I (PI-1)
**Universidade Virtual do Estado de São Paulo — UNIVESP**

---

## 1. 📌 Apresentação do Projeto

O **Conexão Solidária** é uma aplicação web desenvolvida como solução tecnológica para o Projeto Integrador em Computação I da UNIVESP. O sistema tem como objetivo principal apoiar e otimizar a gestão de doações e a operação logística do **Bazar Solidário**, cuja renda é revertida integralmente para ações sociais e amparo a famílias em situação de vulnerabilidade no sertão paraibano.

A plataforma conecta **doadores**, **voluntários** e a **administração da igreja**, oferecendo rastreabilidade completa desde o cadastro de donativos (com modalidades de retirada no local ou entrega presencial), triagem e organização de coletas, até a gestão do estoque de itens disponíveis no bazar.

---

## 2. 🎯 Atendimento aos Requisitos Obrigatórios do Tema (UNIVESP)

O projeto foi construído atendendo rigorosamente ao enunciado oficial do tema do Projeto Integrador:

> *"Desenvolver um software com framework web que utilize banco de dados, inclua script web (Javascript), nuvem, uso de API, acessibilidade, controle de versão e testes. Opcionalmente, incluir análise de dados."*

| Requisito do Tema | Tecnologia / Recurso Utilizado | Descrição da Implementação |
| :--- | :--- | :--- |
| **Framework Web** | **Django (Python 3.13+)** | Arquitetura Model-View-Template (MVT), tratamento seguro de rotas, formulários tipados com sanitização e autenticação robusta. |
| **Banco de Dados** | **PostgreSQL (Produção/Docker) & SQLite3 (Dev/Testes)** | Modelagem relacional (`Doador`, `Doacao`, `Agendamento`) com chaves estrangeiras, transações atômicas e *CheckConstraints* de integridade. |
| **Script Web (JavaScript)** | **TypeScript & JavaScript Moderno (ES2017)** | Scripts assíncronos para consulta de CEP, geração dinâmica de horários, alternância condicional de formulários e controle de acessibilidade (`acessibilidade.js`). |
| **Nuvem (Cloud-Ready)** | **Docker & Docker Compose** | Arquitetura conteinerizada em conformidade com a metodologia *12-Factor App*, preparada para deploy escalável em provedores de nuvem (AWS, GCP, Azure, Render, Fly.io). |
| **Uso de APIs** | **ViaCEP API & Google Maps API** | Consumo assíncrono da API REST do ViaCEP para preenchimento de endereços e integração com Google Maps para geração de rotas de coleta. |
| **Acessibilidade** | **Diretrizes WCAG 2.1 (AA/AAA) & WAI-ARIA** | Modo de Alto Contraste com persistência em `localStorage`, atalho `Alt + C`, Skip Links de navegação por teclado, rótulos explícitos e leituras semânticas para leitores de tela. |
| **Controle de Versão** | **Git & GitHub** | Controle de versão distribuído, histórico de commits semântico e rastreabilidade de código. |
| **Testes Automatizados** | **Django Test Framework** | Suíte de testes automatizados com relatório de auditoria detalhado, validando regras de negócio, segurança (IDOR, CSRF, Staff) e integridade de dados. |

---

## 3. ♿ Acessibilidade e Inclusão Digital (WCAG 2.1)

A acessibilidade digital foi tratada como requisito arquitetural de primeira classe, garantindo que o sistema seja plenamente utilizável por qualquer cidadão, independentemente de suas capacidades visuais, motoras ou cognitivas.

### 🌓 Modo de Alto Contraste (High Contrast Mode)
- **Implementação Técnica:** Desenvolvido no módulo `bazar/static/js/acessibilidade.js` e estilizado em `bazar/static/css/style.css`.
- **Persistência de Sessão:** O estado escolhido pelo usuário é gravado no `localStorage` do navegador sob a chave `conexao_solidaria_alto_contraste`, mantendo o modo ativo durante toda a navegação e entre visitas.
- **Prevenção de FOUC:** Um script síncrono no `<head>` do `base.html` aplica a classe `.alto-contraste` imediatamente antes do render, eliminando cintilação (*Flash of Unstyled Content*).
- **Atalho de Teclado:** O usuário pode alternar o modo a qualquer momento pressionando `Alt + C`.
- **Atributos Dinâmicos:** Os botões de alternância sincronizam o atributo `aria-pressed="true|false"` e títulos de acessibilidade em tempo real.

#### 💡 Justificativa Social e Ergonômica
O Alto Contraste eleva o contraste de cores para a proporção **7:1+** (padrão WCAG AAA), sendo fundamental para:
1. **Pessoas com Baixa Visão e Degeneração Macular:** Facilita a leitura e delimitação dos elementos interativos.
2. **Pessoas com Daltonismo:** Assegura legibilidade independente da percepção de cores (protanopia, deuteranopia e tritanopia).
3. **Pessoas com Fotofobia e Catarata:** O fundo escuro puro reduz o brilho e a fadiga ocular.
4. **Ergonomia e Mobilidade:** Permite o uso confortável do sistema sob incidência direta de luz solar ao ar livre (ex: voluntários realizando coletas na rua).

### ⌨️ Navegação por Teclado e Skip Link
- **Skip to Content:** Link oculto no topo da página que se torna visível ao pressionar a tecla `Tab`, permitindo que usuários de teclado ou leitores de tela pulem direto para o conteúdo principal (`#conteudo-principal`).
- **Foco Visível (`:focus-visible`):** Indicador visual reforçado com anel de foco de alto destaque em todos os botões, links e campos de entrada.

### 🏷️ Semântica e WAI-ARIA nos Formulários e Painéis
- **Associação Estrita de Labels:** Todos os campos de formulário possuem `<label for="ID">` explicitamente vinculado a `<input id="ID">`.
- **Agrupamentos Acessíveis:** Checkboxes e botões de rádio são envolvidos em `role="group"` e `role="radiogroup"` com descrições semânticas.
- **Alertas Dinâmicos:** Mensagens de erro e confirmação utilizam `role="alert"` e `aria-live="polite"` para anúncio imediato por leitores de tela (ex: NVDA, Orca, TalkBack).
- **Abas do Painel Administrativo:** Implementam o padrão WAI-ARIA Tabs (`role="tablist"`, `role="tab"`, `role="tabpanel"`, `aria-selected`), suportando navegação direta pelas setas direcionais (`←` e `→`).

---

## 4. ⚙️ Funcionalidades Principais do Sistema

1. **Página Inicial (Home):** Apresentação do projeto, missão solidária e chamada direta para doação.
2. **Cadastro Inteligente de Doação:**
   - Formulário em etapas lógicas (Doador, Detalhes do Item e Método de Logística).
   - **Consulta de CEP (ViaCEP):** Preenchimento automático de logradouro, bairro, cidade e UF em tempo real.
   - **Horários Condicionais:** Definição de coletas (Segundas e Quartas) ou entregas na igreja (Terças, Quintas e Domingos).
3. **Painel Administrativo Logístico (Área Restrita / Staff):**
   - Central de Coletas com endereço completo, telefone do doador e link direto para rota no Google Maps.
   - Central de Recebimentos na igreja.
   - Gestão de Estoque/Inventário com busca dinâmica e funcionalidade de dar baixa nos itens já destinados.
4. **Catálogo de Itens do Bazar:** Vitrine com os produtos cadastrados e quantidades disponíveis.
5. **Canais de Contato Integrados:** Envio de formulário de contato com disparo de e-mail via SMTP e botão direto para atendimento WhatsApp dinâmico.

---

## 5. 🛡️ Segurança e Regras de Negócio

- **Sanitização de Dados (PII):** Expressões regulares limpam caracteres não-numéricos de telefones e formatam strings antes de persistir no banco.
- **Prevenção de IDOR e Controle de Acesso:** Proteção rigorosa de endpoints com decorators `@login_required` e `@user_passes_test(lambda u: u.is_staff)`.
- **Validações Condicionais no Backend:** Caso o método seja `RETIRADA`, a view e o formulário exigem obrigatoriamente os dados de endereço, garantindo integridade mesmo se o JavaScript for desativado no cliente.
- **Rollback Transacional:** Operações que envolvem criação mútua de `Doacao` e `Agendamento` rodam em blocos atômicos (`transaction.atomic()`).

---

## 6. 🚀 Guia de Instalação e Execução Local

### Pré-requisitos
- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/) instalados;
- [Git](https://git-scm.com/) instalado.

---

### Passo a Passo com Docker (Ambiente Completo com PostgreSQL)

1. **Clonar o Repositório:**
   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd pi1-univesp-main
   ```

2. **Configurar as Variáveis de Ambiente:**
   Copie o arquivo de exemplo para criar o `.env`:
   ```bash
   cp .env.example .env
   ```

3. **Subir os Contêineres da Aplicação e do Banco de Dados:**
   ```bash
   docker compose up -d --build
   ```

4. **Aplicar as Migrações do Banco de Dados:**
   ```bash
   docker compose exec web python manage.py migrate
   ```

5. **Criar o Superusuário Administrador:**
   ```bash
   docker compose exec web python manage.py createsuperuser
   ```
   *(Informe o nome de usuário, e-mail e senha desejados)*

6. **Acessar a Aplicação:**
   - **Aplicação Principal:** [http://localhost:8000](http://localhost:8000)
   - **Central Logística:** [http://localhost:8000/admin-dashboard/](http://localhost:8000/admin-dashboard/)
   - **Painel Django Admin:** [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

### Execução de Testes Automatizados

Para executar toda a suíte de testes de integração e auditoria:

```bash
docker compose exec web python manage.py test -v 2
```

Ou no ambiente Python local (virtualenv):

```bash
python manage.py test -v 2
```

---

### Compilação do Frontend (TypeScript)

A lógica de scripts client-side está modularizada na pasta `bazar/static/js/src/`. Para compilar automaticamente em caso de novas alterações:

```bash
npm install -g typescript
tsc --watch
```

---

## 7. 👥 Informações Acadêmicas

- **Instituição:** Universidade Virtual do Estado de São Paulo (UNIVESP)
- **Curso:** Bacharelado em Ciência de Dados / Tecnologia da Informação / Engenharia de Computação
- **Disciplina:** Projeto Integrador em Computação I (PI-1)
- **Ano / Semestre:** 2026

---
*Conexão Solidária — Transformando doações em esperança para o sertão paraibano.*
