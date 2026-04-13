from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Sum, Max
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Doador, Doacao, Agendamento


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
    doacao = get_object_or_404(Doacao, id=id)
    return render(request, 'bazar/doacao_detalhes.html', {'doacao': doacao})


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
    if request.method == 'POST':
        tipo_entrega = request.POST.get('metodo_entrega', 'RETIRADA')

        nome_doador = (request.POST.get('nome_doador') or '').strip()
        email_doador = (request.POST.get('email_doador') or '').strip()
        telefone_doador = (request.POST.get('telefone_doador') or request.POST.get('whatsapp') or '').strip()
        nome_item = (request.POST.get('nome_item') or '').strip()
        categoria_item = (request.POST.get('categoria_item') or '').strip()
        tamanho_item = (request.POST.get('tamanho_item') or '').strip()
        descricao = (request.POST.get('descricao') or '').strip()

        if not all([nome_doador, email_doador, descricao]):
            messages.error(request, 'Preencha todos os campos obrigatórios.')
            return render(request, 'bazar/cadastrar_doacao.html')

        quantidade_bruta = request.POST.get('quantidade', '1')
        try:
            quantidade = max(1, int(quantidade_bruta))
        except (TypeError, ValueError):
            quantidade = 1

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

        descricao_completa = f"{nome_item} - {descricao}" if nome_item else descricao

        doador, _ = Doador.objects.get_or_create(
            email=email_doador,
            defaults={
                'nome': nome_doador,
                'telefone': telefone_doador or None,
            }
        )

        if doador.nome != nome_doador or doador.telefone != (telefone_doador or None):
            doador.nome = nome_doador
            doador.telefone = telefone_doador or None
            doador.save(update_fields=['nome', 'telefone'])

        doacao = Doacao.objects.create(
            doador=doador,
            nome_item=nome_item or None,
            categoria=categoria_item or None,
            tamanho=tamanho_item or None,
            descricao=descricao_completa,
            quantidade=quantidade,
            tipo_entrega=tipo_entrega,
            endereco_cep=cep_retirada or None,
            endereco_logradouro=endereco_logradouro or None,
            endereco_numero=endereco_numero or None,
            endereco_complemento=endereco_complemento or None,
            endereco_bairro=endereco_bairro or None,
            endereco_cidade=endereco_cidade or None,
            endereco_uf=endereco_uf or None,
            status='PENDENTE',
        )

        Agendamento.objects.create(
            doacao=doacao,
            tipo=tipo_entrega,
            endereco=endereco or None,
            cep_retirada=cep_retirada or None,
            horario_retirada=horario_retirada,
            data=data_agendamento,
            horario=horario_agendamento,
        )

        messages.success(request, 'Doação cadastrada com sucesso!')
        return redirect('doacao_confirmacao')
    
    return render(request, 'bazar/cadastrar_doacao.html')

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