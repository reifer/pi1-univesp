# Contrato Backend-Frontend - PI_UNIVESP (COFRE)

## 1. Mapa de rotas e templates

| Rota | Nome | View | Template principal |
|---|---|---|---|
| / | index | index | bazar/index.html |
| /sobre/ | sobre | sobre | bazar/sobre.html |
| /contato/ | contato | contato | bazar/contato.html |
| /doacoes/ | doacoes_list | doacoes_list | bazar/doacoes.html |
| /doacoes/<id>/ | doacao_detalhe | doacao_detalhe | bazar/doacao_detalhes.html |
| /doar/ | cadastrar_doacao | cadastrar_doacao | bazar/cadastrar_doacao.html |
| /doar/confirmacao/ | doacao_confirmacao | doacao_confirmacao | bazar/doacao_confirmacao.html |
| /painel/ | admin_dashboard | admin_dashboard | bazar/admin_dashboard.html |
| /painel/deletar/<pk>/ | deletar_doacao | deletar_doacao | redirect para painel |
| /painel/status/<pk>/ | atualizar_status_doacao | atualizar_status_doacao | redirect para painel |
| /painel/baixa/<pk>/ | dar_baixa_doacao | dar_baixa_doacao | redirect para painel |

Observacao de estrutura:
- Quase todas as paginas em bazar/templates/bazar estendem bazar/base.html.
- base.html inclui bazar/navbar.html.

---

## 2. Contrato por pagina

## 2.1 bazar/base.html

### Contexto recebido
- Nao recebe dicionario especifico da view.
- Usa variaveis globais do Django template context:
  - user.is_authenticated
  - request.resolver_match.url_name (consumido no include navbar).

### Formularios e envio
- Nenhum formulario proprio.

### Loops e condicionais
- Nao ha loops.
- Renderiza bloco dinamico: block content.
- Include dinamico: include bazar/navbar.html.

### Integracoes externas
- Tailwind via CDN.
- Google Fonts.
- Script local de animacao com IntersectionObserver.

---

## 2.2 bazar/navbar.html

### Contexto recebido
- user.is_authenticated
- request.resolver_match.url_name

### Formularios e envio
1. Logout
- action: rota logout
- method: POST
- campos:
  - csrfmiddlewaretoken (automatico)
- obrigatorios backend:
  - csrf valido

### Loops e condicionais
- If para destacar menu ativo por request.resolver_match.url_name.
- If para mostrar botao Sair apenas autenticado.
- If no link Area Restrita:
  - autenticado -> admin_dashboard
  - anonimo -> login

### Integracoes externas
- Nenhuma.

---

## 2.3 bazar/index.html

### Contexto recebido
- doacoes: QuerySet de Doacao (status PENDENTE, max 6) enviado pela view index.
- Observacao: atualmente o template nao faz loop em doacoes, mas a variavel e enviada.

### Formularios e envio
- Nenhum formulario.
- Link CTA para rota cadastrar_doacao.

### Loops e condicionais
- Sem for/if de dados de backend para conteudo principal.

### Integracoes externas
- Nenhuma.

---

## 2.4 bazar/sobre.html

### Contexto recebido
- Nenhuma variavel especifica da view sobre.

### Formularios e envio
- Nenhum.

### Loops e condicionais
- Nao ha loops/ifs de backend.

### Integracoes externas
- Nenhuma.

---

## 2.5 bazar/contato.html

### Contexto recebido
- messages (framework de mensagens).

### Formularios e envio
1. Formulario de contato
- action: vazio (submete para a propria rota /contato/)
- method: POST
- campos:
  - nome (required)
  - email (required)
  - telefone (opcional)
  - assunto (required)
  - mensagem (required)
  - csrfmiddlewaretoken
- obrigatorios para nao falhar no HTML:
  - nome, email, assunto, mensagem
- observacao importante de contrato:
  - a view contato apenas renderiza template e nao processa POST no backend.
  - para funcionalidade real, frontend deve aguardar implementacao backend ou endpoint dedicado.

### Loops e condicionais
- if messages
- for message in messages
- if message.tags == success

### Integracoes externas
- Nenhuma.

---

## 2.6 bazar/cadastrar_doacao.html

### Contexto recebido
- messages
- sem dicionario adicional explicito na view para GET.

### Formularios e envio
1. Cadastro de doacao
- action: rota cadastrar_doacao
- method: POST
- campos enviados (name):
  - nome_doador
  - email_doador
  - telefone_doador
  - nome_item
  - categoria_item
  - tamanho_item
  - quantidade
  - descricao
  - metodo_entrega (RETIRADA ou ENTREGA)
  - cep_retirada
  - endereco_retirada
  - numero_retirada
  - complemento_retirada
  - bairro_retirada
  - cidade_retirada
  - uf_retirada
  - data_retirada
  - horario_retirada
  - data_sugerida
  - horario_sugerido
  - csrfmiddlewaretoken

### Campos obrigatorios para backend nao retornar erro
Regra geral:
- nome_doador, email_doador, descricao

Se metodo_entrega = RETIRADA:
- endereco_retirada (logradouro auto)
- numero_retirada
- bairro_retirada
- cidade_retirada
- uf_retirada (2 chars)
- cep_retirada (formato 00000-000)
- data_retirada (nao passada, apenas segunda ou quarta)
- horario_retirada (09:00 ate 17:00)

Se metodo_entrega = ENTREGA:
- data_sugerida
- horario_sugerido
- data_sugerida deve cair em terca, quinta ou domingo

### Loops e condicionais
- if messages / for message in messages
- bloco de campos mostrado/escondido via JS conforme metodo_entrega.

### Integracoes externas
1. ViaCEP
- endpoint: https://viacep.com.br/ws/{cep}/json/
- gatilho: blur do campo id cep-retirada
- IDs manipulados:
  - leitura: cep-retirada
  - preenchimento automatico: endereco-retirada, bairro-retirada, cidade-retirada, uf-retirada
- validacoes frontend:
  - CEP com 8 digitos
  - mascara 00000-000

2. Regras de calendario e horario (frontend)
- RETIRADA:
  - id data-retirada: apenas segunda e quarta
  - id horario-retirada: 09:00 a 17:00
- ENTREGA:
  - id data-sugerida: apenas domingo, terca, quinta
  - id horario-sugerido: opcoes dinamicas por dia

---

## 2.7 bazar/doacoes.html

### Contexto recebido
- doacoes: QuerySet de Doacao (select_related com doador e agendamento)
- query: string de busca opcional

### Atributos acessados no template
- doacao.id
- doacao.get_tipo_entrega_display
- doacao.status
- doacao.descricao
- doacao.quantidade

### Formularios e envio
- Nenhum formulario.
- Link de acao para rota doacao_detalhe com id.

### Loops e condicionais
- for doacao in doacoes
- empty quando lista vazia
- condicionais por status para badge visual:
  - PENDENTE
  - AGENDADA
  - CONCLUIDA
  - fallback para demais status

### Integracoes externas
- Nenhuma.

---

## 2.8 bazar/doacao_detalhes.html

### Contexto recebido
- doacao: objeto Doacao vindo de get_object_or_404

### Atributos acessados
Doacao:
- id
- descricao
- quantidade
- tipo_entrega
- get_tipo_entrega_display
- get_status_display

Relacionamento doador:
- doacao.doador.telefone
- doacao.doador.email

Relacionamento agendamento:
- doacao.agendamento
- doacao.agendamento.get_tipo_display
- doacao.agendamento.data
- doacao.agendamento.horario
- doacao.agendamento.endereco

### Formularios e envio
- Nenhum formulario.
- Link mailto dinamico para contato por email.

### Loops e condicionais
- if doacao.doador.telefone
- if doacao.doador.email
- if not telefone and not email
- if doacao.agendamento
- if doacao.tipo_entrega == ENTREGA

### Integracoes externas
- mailto para cliente de email.

---

## 2.9 bazar/doacao_confirmacao.html

### Contexto recebido
- Nenhuma variavel especifica.

### Formularios e envio
- Nenhum formulario.
- Dois links de navegacao:
  - index
  - cadastrar_doacao

### Loops e condicionais
- Nenhum.

### Integracoes externas
- Nenhuma.

---

## 2.10 bazar/admin_dashboard.html

### Contexto recebido (view admin_dashboard)
- doacoes_retirada: QuerySet de Doacao
  - filtro: tipo_entrega RETIRADA e status em PENDENTE/AGENDADA
- doacoes_entrega: QuerySet de Doacao
  - filtro: tipo_entrega ENTREGA e status em PENDENTE/AGENDADA
- estoque_resumo: QuerySet agregado (values + annotate)
  - campos: nome_item, categoria, tamanho, quantidade_total, data_entrada
  - origem: apenas Doacao com status CONCLUIDA
- doacoes_concluidas: QuerySet de Doacao
  - origem: apenas status CONCLUIDA
- estoque_baixado: QuerySet agregado
  - origem: status BAIXADA
- estoque_q: string de busca GET
- estoque_total_disponivel: integer (count de CONCLUIDA apos filtro)

### Atributos acessados no template
Em doacoes_retirada e doacoes_entrega:
- d.id
- d.nome_item
- d.descricao
- d.doador.nome
- d.doador.telefone
- d.agendamento.data
- d.agendamento.horario
- d.agendamento.horario_retirada
- d.get_status_display

Endereco estruturado/fallback legado:
- d.endereco_logradouro
- d.endereco_numero
- d.endereco_bairro
- d.endereco_cidade
- d.endereco_uf
- d.endereco_cep
- fallback: d.agendamento.endereco e d.agendamento.cep_retirada

Em estoque_resumo:
- item.nome_item
- item.categoria
- item.tamanho
- item.quantidade_total
- item.data_entrada

Em doacoes_concluidas:
- d.id, d.nome_item, d.descricao, d.categoria, d.tamanho, d.quantidade, d.data_criacao, d.tipo_entrega

Em estoque_baixado:
- item.nome_item
- item.quantidade_total

### Formularios e envio
1. Logout (cabecalho)
- action: rota logout
- method: POST
- campos:
  - csrfmiddlewaretoken

2. Atualizar status (coletado/recebido)
- action: rota atualizar_status_doacao com pk
- method: POST
- campos:
  - status (hidden, valor CONCLUIDA)
  - csrfmiddlewaretoken
- obrigatorios backend:
  - status valido em STATUS_CHOICES

3. Excluir doacao
- action: rota deletar_doacao com pk
- method: POST
- campos:
  - csrfmiddlewaretoken

4. Busca de inventario
- action: pagina atual
- method: GET
- campos:
  - estoque_q (opcional)

5. Dar baixa
- action: rota dar_baixa_doacao com pk
- method: POST
- campos:
  - csrfmiddlewaretoken
- obrigatorio backend:
  - doacao alvo precisa estar com status CONCLUIDA

### Loops e condicionais
- if messages / for message in messages
- filtro de mensagem na propria view do template:
  - oculta mensagem de sucesso de cadastro de doacao
- loops principais:
  - for d in doacoes_retirada
  - for d in doacoes_entrega
  - for item in estoque_resumo
  - for d in doacoes_concluidas
  - for item in estoque_baixado
- condicionais adicionais:
  - if d.endereco_numero
  - if d.endereco_bairro
  - if d.tipo_entrega == RETIRADA
  - if estoque_baixado
  - empty para tabelas vazias

### Integracoes externas
1. Google Maps
- nao e script JS, e link gerado por template para rota.
- URL base: https://www.google.com/maps/search/?api=1&query=...
- campos usados na query:
  - endereco_logradouro, endereco_numero, endereco_bairro, endereco_cidade, endereco_uf, endereco_cep
  - fallback para agendamento.endereco e agendamento.cep_retirada

2. Tabs internas do painel
- script local no fim do template.
- IDs/atributos usados:
  - botoes com data-tab-target
  - paineis com id logistica-tab e inventario-tab

---

## 3. Contrato de tipos para frontend

## 3.1 Tipo Doacao (uso em listagens)
- id: integer
- nome_item: string ou null
- categoria: string ou null
- tamanho: string ou null
- descricao: string
- quantidade: integer
- tipo_entrega: enum RETIRADA | ENTREGA
- status: enum PENDENTE | AGENDADA | CONCLUIDA | BAIXADA | CANCELADA
- endereco_cep: string ou null
- endereco_logradouro: string ou null
- endereco_numero: string ou null
- endereco_complemento: string ou null
- endereco_bairro: string ou null
- endereco_cidade: string ou null
- endereco_uf: string ou null
- data_criacao: datetime
- doador: objeto Doador (quando select_related)
- agendamento: objeto Agendamento (quando select_related)

## 3.2 Tipo Doador
- nome: string
- telefone: string ou null
- email: string

## 3.3 Tipo Agendamento
- tipo: enum RETIRADA | ENTREGA
- data: date ou null
- horario: time ou null
- endereco: string ou null
- cep_retirada: string ou null
- horario_retirada: time ou null

## 3.4 Tipo EstoqueResumo (agregado)
- nome_item: string ou null
- categoria: string ou null
- tamanho: string ou null
- quantidade_total: integer
- data_entrada: datetime

---

## 4. Checklist rapido para reescrever frontend sem quebrar backend

- Manter nomes de campos do formulario de doacao exatamente iguais.
- Garantir que o envio para cadastrar_doacao continue em POST com csrf.
- Se metodo_entrega for RETIRADA, enviar todos os campos obrigatorios de endereco/data/horario.
- Se metodo_entrega for ENTREGA, enviar data_sugerida e horario_sugerido validos.
- Nas acoes do painel, manter rotas de POST com pk e hidden status quando aplicavel.
- Preservar fallback de endereco legado para registros antigos no inventario/logistica.
- Preservar estoque_q como parametro GET para busca de inventario.

---

## 5. Observacoes de risco de integracao

1. Formulario de contato
- UI envia POST, mas a view contato atual nao salva nem encaminha dados.
- Necessita endpoint/servico para operacionalizar envio.

2. Pagina index
- View ainda envia doacoes no contexto, mas template atual nao consome.
- Pode ser removido do contexto futuramente para reduzir custo de query.

3. Acesso ao painel
- Depende de autenticacao e is_staff.
- Frontend deve tratar redirecionamento para login quando necessario.
