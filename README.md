# Bazar Solidário - Documentação Técnica e Onboarding

Este documento reflete a estrutura técnica exata do projeto de doações, detalhando as regras de negócios, tecnologias implementadas e infraestrutura, garantindo integração rápida para novos desenvolvedores.

## 1. � Stack Principal

- **Backend:** Python 3.13+ e Django (Gunicorn em produção).
- **Frontend:** TypeScript (Target ES2017 para o client-side) e Tailwind CSS (via CDN).
- **Banco de Dados:** SQLite3 (Ambiente Dev) e PostgreSQL (via psycopg2 para Prod).
- **DevOps/Infra:** Contêineres com Docker e orquestração Docker Compose.
- **Ambientes:** Hierarquia controlada: Dev (local) -> Homologação -> Prod.
- **Gerenciamento de Configuração:** `python-dotenv` para isolamento de senhas e travas de ambiente.

---

## 2. ⚙️ Funcionalidades, Regras de Negócio e UX

A plataforma foi construída sob rigoroso controle transacional e experiência do usuário:

### Validação de Formulários e UX Dinâmica
- **Busca Assíncrona de CEP (ViaCEP):** Ao preencher 8 dígitos no campo `inputCepRetirada`, o sistema desabilita os sub-campos de endereço, inicia um estado de "loading", pesquisa na API ViaCEP remotamente e trata retornos de erro (`data.erro`) com validação de existência de CEP no banco central, limpando os dados se inválido e emitindo alertas de fallback dinâmicos.
- **Horários Flexíveis (Datalist):** O antigo select rigoroso foi substituído por uma arquitetura híbrida de `<input list="opcoes-horario">`, dando liberdade ao usuário para digitar o horário exato ou selecionar sugestões geradas via TypeScript de 30 em 30 minutos, mantendo compatibilidade e validação de limite.
- **Condicionais Dinâmicas (Toggles de UI):** A interface ativa/desativa requerimentos e exibições dependendo de escolhas do usuário (Ex: esconder campos de endereço quando marcado "ENTREGA" e exibi-los sob "RETIRADA").
- **Tratativas de Data e Horário:** A interface impede visualmente seleção de datas defasadas e domingos, gerenciando arrays de feedback.

### Regras de Domínio e Persistência (Backend)
- **Sanitização de PII (RegEx):** O método `clean_telefone` no `bazar/forms.py` limpa todos os caracteres não numéricos (`\D`) via expressões regulares, garantindo que o banco armazene apenas o formato telefônico bruto para evitar injeções.
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

---

## 6. 💻 Desenvolvimento Frontend com TypeScript

O projeto utiliza TypeScript para modernizar e trazer tipagem à lógica de *client-side*. Notou alguns arquivos duplos? Não é lixo ou código esquecido! Abaixo a explicação da organização:

- **Pasta `src/`:** Contém o código-fonte original em TypeScript (`.ts`). **Toda a edição de lógica do frontend deve ser feita aqui.**
- **Pasta `compiled/`:** Contém os arquivos distribuíveis em JavaScript puro (`.js`). Esses são os arquivos reais que o Django consome e serve para o navegador. **Eles não devem ser editados diretamente**, pois são gerados e sobrescritos automaticamente pelo compilador.

### 🔄 Comando de Build (Sincronia TS ➔ JS)
Para manter o fluxo de desenvolvimento ativo sem se preocupar com compilação manual a cada salvamento, deixe registrado este comando essencial rodando em um terminal à parte:

```bash
tsc --watch
```
Isso vai assegurar que qualquer update feito em `horario.ts` ou `cep.ts` reflita instantaneamente sobre os arquivos que o navegador vai enxergar.

---

## 7. 🧪 Guia de Testes e Qualidade

### Como executar os testes

Rodar a suíte completa com saída detalhada:

```bash
python manage.py test -v 2
```

Rodar apenas o arquivo de integração em modo auditoria:

```bash
python manage.py test bazar.testes_completos -v 2
```

### O que os 18 testes validam

| Teste | Validação |
|---|---|
| `test_acesso_negado_ao_painel_sem_login` | Bloqueia acesso ao painel para visitante não autenticado. |
| `test_acesso_negado_ao_painel_sem_staff` | Bloqueia acesso ao painel para usuário comum autenticado. |
| `test_usuario_comum_nao_exclui_doacao_de_terceiro` | Previne IDOR em exclusão via URL. |
| `test_usuario_comum_nao_altera_status_de_doacao` | Previne alteração indevida de status via URL. |
| `test_usuario_comum_nao_da_baixa_em_doacao_de_terceiro` | Previne baixa indevida de estoque via URL. |
| `test_campo_legado_e_scripts_sao_escapados_no_detalhe` | Garante escape de scripts e ignora campo legado `tamanho`. |
| `test_cadastro_rejeita_cep_invalido_no_backend` | Valida rejeição de CEP inválido no backend. |
| `test_cadastro_aceita_horario_coleta_no_formato_hh_mm` | Confirma persistência de horário válido em `HH:MM`. |
| `test_cadastro_rejeita_horario_coleta_fora_do_padrao` | Rejeita horário fora do padrão esperado. |
| `test_fluxo_completo_exibe_dados_corretos_no_painel` | Valida o fluxo feliz até o painel com descrição, quantidade e categoria. |
| `test_modelo_rejeita_doacao_sem_doador` | Previne criação de doação sem doador. |
| `test_modelo_rejeita_doacao_sem_descricao` | Previne criação de doação sem descrição. |
| `test_modelo_define_status_padrao_pendente` | Confirma o status padrão `PENDENTE`. |
| `test_fluxo_pendente_permanece_com_status_padrao_no_cadastro_publico` | Garante que o cadastro público salva com status padrão. |
| `test_staff_pode_concluir_doacao` | Verifica a conclusão de doação pelo staff. |
| `test_staff_pode_dar_baixa_em_doacao_concluida` | Verifica a baixa de estoque pelo staff. |
| `test_validacao_endereco_retirada_sem_campos_obrigatorios` | Valida endereço obrigatório no fluxo de retirada. |
| `test_rollback_total_quando_agendamento_falha` | Garante rollback total quando o agendamento falha. |

### Leitura do relatório no terminal

Ao executar com `-v 2`, o Django exibirá cada teste em português e marcará o resultado com `... ok` ou `... FAIL`, deixando a auditoria de qualidade fácil de acompanhar no terminal.
