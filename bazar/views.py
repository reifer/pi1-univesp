from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.db.models import Q, Sum, Max
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Doador, Doacao, Agendamento
from .forms import DoadorForm, DoacaoForm


def parse_horario_sugerido(raw_value):
    """Aceita HH:MM e intervalos no formato HH:MM - HH:MM."""
    horario_bruto = (raw_value or '').strip()
    if not horario_bruto:
        raise ValueError('Horário vazio')

    horario_base = horario_bruto.split('-')[0].strip()
    return datetime.strptime(horario_base, '%H:%M').time()

def index(request):
    doacoes = Doacao.objects.filter(status='PENDENTE').order_by('-data_criacao')[:6]
    return render(request, 'bazar/index.html', {'doacoes': doacoes})


def sobre(request):
    return render(request, 'bazar/sobre.html')


def contato(request):
    if request.method == 'POST':
        nome = (request.POST.get('nome') or '').strip()
        email = (request.POST.get('email') or '').strip()
        assunto = (request.POST.get('assunto') or '').strip()
        mensagem = (request.POST.get('mensagem') or '').strip()

        if not all([nome, email, assunto, mensagem]):
            messages.error(request, 'Preencha todos os campos obrigatórios para enviar sua mensagem.')
            return render(request, 'bazar/contato.html')

        messages.success(request, 'Mensagem enviada! Entraremos em contato em breve.')
        return redirect('contato')

    return render(request, 'bazar/contato.html')

@login_required
def doacoes_list(request):
    query = request.GET.get('q')
    todas_doacoes = Doacao.objects.select_related('doador', 'agendamento').order_by('-data_criacao')

    if query:
        todas_doacoes = todas_doacoes.filter(
            Q(descricao__icontains=query) | Q(doador__nome__icontains=query)
        )

    return render(request, 'bazar/doacoes.html', {
        'doacoes': todas_doacoes,
        'query': query
    })

def doacao_detalhe(request, id):
    can_view_sensitive = request.user.is_authenticated and request.user.is_staff

    if can_view_sensitive:
        doacao = get_object_or_404(
            Doacao.objects.select_related('doador', 'agendamento'),
            id=id,
        )
    else:
        # Público só pode acessar doações disponíveis no catálogo público.
        doacao = get_object_or_404(
            Doacao.objects.select_related('doador', 'agendamento').filter(status='PENDENTE'),
            id=id,
        )

    return render(
        request,
        'bazar/doacao_detalhes.html',
        {
            'doacao': doacao,
            'can_view_sensitive': can_view_sensitive,
        },
    )


def doacao_confirmacao(request):
    return render(request, 'bazar/doacao_confirmacao.html')

# VIEW PÚBLICA - Cadastro de Doações (sem login_required)
def cadastrar_doacao(request):
    """
    View pública para cadastro de doações.
    Aceita método RETIRADA e ENTREGA.
    Para retirada, coleta endereço estruturado via CEP, data e horário.
    Para entrega, valida janela da igreja (terça, quinta e domingo).
    """
    doador_form = DoadorForm()
    doacao_form = DoacaoForm()

    if request.method == 'POST':
        tipo_entrega = request.POST.get('metodo_entrega', 'RETIRADA')

        nome_doador = (request.POST.get('nome_doador') or '').strip()
        email_doador = (request.POST.get('email_doador') or '').strip().lower()
        telefone_doador = (request.POST.get('telefone_doador') or request.POST.get('whatsapp') or '').strip()
        nome_item = (request.POST.get('nome_item') or '').strip()
        categorias_selecionadas = request.POST.getlist('categoria')
        categoria_item = ', '.join(categorias_selecionadas) if categorias_selecionadas else ''
        tamanho_item = (request.POST.get('tamanho_item') or '').strip()
        descricao = (request.POST.get('descricao') or '').strip()

        doador_form = DoadorForm(data={
            'nome': nome_doador,
            'email': email_doador,
            'telefone': telefone_doador,
        })

        descricao_completa = f"{nome_item} - {descricao}" if nome_item else descricao
        doacao_form = DoacaoForm(data={
            'nome_item': nome_item,
            'categoria': categoria_item,
            'tamanho': tamanho_item,
            'descricao': descricao_completa,
            'quantidade': request.POST.get('quantidade', '1'),
            'tipo_entrega': tipo_entrega,
            'endereco_cep': (request.POST.get('cep_retirada') or '').strip(),
            'endereco_logradouro': (request.POST.get('endereco_retirada') or '').strip(),
            'endereco_numero': (request.POST.get('numero_retirada') or '').strip(),
            'endereco_complemento': (request.POST.get('complemento_retirada') or '').strip(),
            'endereco_bairro': (request.POST.get('bairro_retirada') or '').strip(),
            'endereco_cidade': (request.POST.get('cidade_retirada') or '').strip(),
            'endereco_uf': (request.POST.get('uf_retirada') or '').strip(),
        })

        if not (doador_form.is_valid() and doacao_form.is_valid()):
            messages.error(request, 'Preencha corretamente os campos obrigatórios.')
            for erros in doador_form.errors.values():
                for erro in erros:
                    messages.error(request, erro)
            for erros in doacao_form.errors.values():
                for erro in erros:
                    messages.error(request, erro)
            return render(request, 'bazar/cadastrar_doacao.html', {'doador_form': doador_form, 'doacao_form': doacao_form})

        endereco = None
        cep_retirada = None
        endereco_logradouro = None
        endereco_numero = None
        endereco_complemento = None
        endereco_bairro = None
        endereco_cidade = None
        endereco_uf = None
        horario_retirada = None
        data_agendamento = None
        horario_agendamento = None

        if tipo_entrega == 'RETIRADA':
            endereco_logradouro = (request.POST.get('endereco_retirada') or '').strip()
            endereco_numero = (request.POST.get('numero_retirada') or '').strip()
            endereco_complemento = (request.POST.get('complemento_retirada') or '').strip()
            endereco_bairro = (request.POST.get('bairro_retirada') or '').strip()
            endereco_cidade = (request.POST.get('cidade_retirada') or '').strip()
            endereco_uf = (request.POST.get('uf_retirada') or '').strip().upper()
            cep_retirada = (request.POST.get('cep_retirada') or '').strip()
            data_retirada_str = (request.POST.get('data_retirada') or '').strip()
            horario_retirada_str = (request.POST.get('horario_retirada') or '').strip()

            if not all([
                endereco_logradouro,
                endereco_numero,
                endereco_bairro,
                endereco_cidade,
                endereco_uf,
                cep_retirada,
                data_retirada_str,
                horario_retirada_str,
            ]):
                messages.error(request, 'Para retirada, informe CEP, logradouro, número, bairro, cidade/UF, data e horário para coleta.')
                return render(request, 'bazar/cadastrar_doacao.html')

            if len(cep_retirada) != 9 or cep_retirada[5] != '-':
                messages.error(request, 'CEP inválido. Use o formato 00000-000.')
                return render(request, 'bazar/cadastrar_doacao.html')

            if len(endereco_uf) != 2:
                messages.error(request, 'UF inválida para retirada.')
                return render(request, 'bazar/cadastrar_doacao.html')

            try:
                data_agendamento = datetime.strptime(data_retirada_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, 'Formato de data de retirada inválido.')
                return render(request, 'bazar/cadastrar_doacao.html')

            if data_agendamento < datetime.today().date():
                messages.error(request, 'Não é permitido selecionar datas passadas para retirada.')
                return render(request, 'bazar/cadastrar_doacao.html')

            if data_agendamento.weekday() not in {0, 2}:
                messages.error(request, 'Nossa equipe realiza coletas apenas às Segundas e Quartas-feiras.')
                return render(request, 'bazar/cadastrar_doacao.html')

            try:
                horario_retirada = datetime.strptime(horario_retirada_str, '%H:%M').time()
            except ValueError:
                messages.error(request, 'Formato de horário de retirada inválido.')
                return render(request, 'bazar/cadastrar_doacao.html')

            if not (datetime.strptime('09:00', '%H:%M').time() <= horario_retirada <= datetime.strptime('17:00', '%H:%M').time()):
                messages.error(request, 'Para retirada, o horário deve estar entre 09:00 e 17:00.')
                return render(request, 'bazar/cadastrar_doacao.html')

            endereco = f"{endereco_logradouro}, {endereco_numero}"
            if endereco_complemento:
                endereco = f"{endereco} - {endereco_complemento}"
        elif tipo_entrega == 'ENTREGA':
            data_sugerida_str = (request.POST.get('data_sugerida') or '').strip()
            horario_sugerido_str = (request.POST.get('horario_sugerido') or '').strip()

            if not all([data_sugerida_str, horario_sugerido_str]):
                messages.error(request, 'Para entrega, informe data e horário.')
                return render(request, 'bazar/cadastrar_doacao.html')

            try:
                data_agendamento = datetime.strptime(data_sugerida_str, '%Y-%m-%d').date()
                horario_agendamento = parse_horario_sugerido(horario_sugerido_str)
            except ValueError:
                messages.error(request, 'Formato de data/horário inválido.')
                return render(request, 'bazar/cadastrar_doacao.html')

            # Segurança contra bypass de frontend: apenas terça, quinta e domingo.
            if data_agendamento.weekday() not in {1, 3, 6}:
                messages.error(
                    request,
                    'Ops! Entregas apenas às Terças, Quintas e Domingos. Por favor, escolha um desses dias no calendário.'
                )
                return render(request, 'bazar/cadastrar_doacao.html')

        doador_data = doador_form.cleaned_data
        doacao_data = doacao_form.cleaned_data

        with transaction.atomic():
            doador, _ = Doador.objects.get_or_create(
                email=doador_data['email'],
                defaults={
                    'nome': doador_data['nome'],
                    'telefone': doador_data.get('telefone'),
                }
            )

            if doador.nome != doador_data['nome'] or doador.telefone != doador_data.get('telefone'):
                doador.nome = doador_data['nome']
                doador.telefone = doador_data.get('telefone')
                doador.save(update_fields=['nome', 'telefone'])

            doacao = doacao_form.save(commit=False)
            doacao.doador = doador
            doacao.status = 'PENDENTE'
            doacao.endereco_cep = cep_retirada or doacao_data.get('endereco_cep')
            doacao.endereco_logradouro = endereco_logradouro or doacao_data.get('endereco_logradouro')
            doacao.endereco_numero = endereco_numero or doacao_data.get('endereco_numero')
            doacao.endereco_complemento = endereco_complemento or doacao_data.get('endereco_complemento')
            doacao.endereco_bairro = endereco_bairro or doacao_data.get('endereco_bairro')
            doacao.endereco_cidade = endereco_cidade or doacao_data.get('endereco_cidade')
            doacao.endereco_uf = endereco_uf or doacao_data.get('endereco_uf')
            doacao.save()

            Agendamento.objects.create(
                doacao=doacao,
                tipo=tipo_entrega,
                horario_retirada=horario_retirada,
                data=data_agendamento,
                horario=horario_agendamento,
            )

        messages.success(request, 'Doação cadastrada com sucesso!')
        return redirect('doacao_confirmacao')

    return render(request, 'bazar/cadastrar_doacao.html', {'doador_form': doador_form, 'doacao_form': doacao_form})

# Função helper para verificar se é staff
def user_is_staff(user):
    return user.is_staff

# VIEW PROTEGIDA - Painel Administrativo (apenas staff)
@login_required
@user_passes_test(user_is_staff)
def admin_dashboard(request):
    """
    Painel administrativo para gerenciar logística de doações.
    Apenas acessível para usuários autenticados com is_staff=True.
    """
    doacoes_retirada = Doacao.objects.select_related('doador', 'agendamento').filter(
        tipo_entrega='RETIRADA',
        status__in=['PENDENTE', 'AGENDADA']
    ).order_by('-data_criacao')
    doacoes_entrega = Doacao.objects.select_related('doador', 'agendamento').filter(
        tipo_entrega='ENTREGA',
        status__in=['PENDENTE', 'AGENDADA']
    ).order_by('-data_criacao')

    estoque_q = (request.GET.get('estoque_q') or '').strip()
    estoque_disponivel = Doacao.objects.filter(status='CONCLUIDA')

    if estoque_q:
        estoque_disponivel = estoque_disponivel.filter(
            Q(nome_item__icontains=estoque_q)
            | Q(categoria__icontains=estoque_q)
            | Q(tamanho__icontains=estoque_q)
            | Q(descricao__icontains=estoque_q)
        )

    estoque_resumo = estoque_disponivel.values('nome_item', 'categoria', 'tamanho').annotate(
        quantidade_total=Sum('quantidade'),
        data_entrada=Max('data_criacao'),
    ).order_by('nome_item', 'categoria', 'tamanho')

    estoque_total_disponivel = estoque_disponivel.count()

    doacoes_concluidas = estoque_disponivel.select_related('doador').order_by('-data_criacao')

    estoque_baixado = Doacao.objects.filter(status='BAIXADA').values('nome_item', 'categoria', 'tamanho').annotate(
        quantidade_total=Sum('quantidade'),
        data_entrada=Max('data_criacao'),
    ).order_by('nome_item', 'categoria', 'tamanho')[:10]

    return render(
        request,
        'bazar/admin_dashboard.html',
        {
            'doacoes_retirada': doacoes_retirada,
            'doacoes_entrega': doacoes_entrega,
            'estoque_resumo': estoque_resumo,
            'doacoes_concluidas': doacoes_concluidas,
            'estoque_baixado': estoque_baixado,
            'estoque_q': estoque_q,
            'estoque_total_disponivel': estoque_total_disponivel,
        }
    )

@login_required
@user_passes_test(user_is_staff)
def deletar_doacao(request, pk):
    """
    Deletar uma doação (apenas staff).
    """
    if request.method == 'POST':
        doacao = get_object_or_404(Doacao, pk=pk)
        doacao.delete()
        messages.success(request, 'Doação removida com sucesso.')
    return redirect('admin_dashboard')


@login_required
@user_passes_test(user_is_staff)
def atualizar_status_doacao(request, pk):
    if request.method != 'POST':
        return redirect('admin_dashboard')

    doacao = get_object_or_404(Doacao, pk=pk)
    novo_status = request.POST.get('status')
    status_validos = {choice[0] for choice in Doacao.STATUS_CHOICES}

    if novo_status not in status_validos:
        messages.error(request, 'Status inválido.')
        return redirect('admin_dashboard')

    doacao.status = novo_status
    doacao.save(update_fields=['status'])
    messages.success(request, f'Status da doação #{doacao.pk} atualizado para {doacao.get_status_display()}.')
    return redirect('admin_dashboard')


@login_required
@user_passes_test(user_is_staff)
def dar_baixa_doacao(request, pk):
    if request.method != 'POST':
        return redirect('admin_dashboard')

    doacao = get_object_or_404(Doacao, pk=pk)
    if doacao.status != 'CONCLUIDA':
        messages.error(request, 'Apenas itens concluídos podem receber baixa de estoque.')
        return redirect('admin_dashboard')

    doacao.status = 'BAIXADA'
    doacao.save(update_fields=['status'])
    messages.success(request, f'Baixa de estoque registrada para a doação #{doacao.pk}.')
    return redirect('admin_dashboard')