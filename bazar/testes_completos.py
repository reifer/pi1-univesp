from datetime import date, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from .forms import DoacaoForm
from .models import Agendamento, Doacao, Doador


def proxima_data_dia_semana(alvo_dia_semana):
    """Retorna a próxima data para um dia da semana (0=segunda ... 6=domingo)."""
    hoje = date.today()
    dias_ate = (alvo_dia_semana - hoje.weekday()) % 7
    if dias_ate == 0:
        dias_ate = 7
    return hoje + timedelta(days=dias_ate)


class TestesCompletosDoBazar(TestCase):
    def setUp(self):
        self.Usuario = get_user_model()
        self.usuario_staff = self.Usuario.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='password123',
            is_staff=True,
        )
        self.usuario_comum = self.Usuario.objects.create_user(
            username='visitor',
            email='visitor@example.com',
            password='password123',
            is_staff=False,
        )

        self.cliente_visitante = Client()
        self.cliente_staff = Client()
        self.cliente_comum = Client()
        self.cliente_staff.force_login(self.usuario_staff)
        self.cliente_comum.force_login(self.usuario_comum)

        self.url_painel = reverse('admin_dashboard')
        self.url_cadastrar = reverse('cadastrar_doacao')

    def _payload_retirada(self, **sobrescritas):
        payload = {
            'nome_doador': 'Maria Silva',
            'email_doador': 'maria@example.com',
            'telefone_doador': '(11) 98888-7777',
            'nome_item': 'Camiseta',
            'categoria': ['Roupa'],
            'descricao': 'Em bom estado',
            'quantidade': '2',
            'metodo_entrega': 'RETIRADA',
            'cep_retirada': '01001-000',
            'endereco_retirada': 'Rua das Flores',
            'numero_retirada': '120',
            'complemento_retirada': 'Casa',
            'bairro_retirada': 'Centro',
            'cidade_retirada': 'Sao Paulo',
            'uf_retirada': 'SP',
            'data_retirada': proxima_data_dia_semana(0).isoformat(),
            'horario_coleta': '10:00',
        }
        payload.update(sobrescritas)
        return payload

    def test_acesso_negado_ao_painel_sem_login(self):
        """Valida se usuários não autenticados são redirecionados ao tentar abrir o painel."""
        response = self.cliente_visitante.get(self.url_painel)

        self.assertEqual(
            response.status_code,
            302,
            'FALHA: o painel não redirecionou o visitante sem login. Verifique o decorator de autenticação em admin_dashboard.',
        )
        self.assertIn(
            '/accounts/login/',
            response.url,
            'FALHA: o redirecionamento do painel sem login não apontou para /accounts/login/. Verifique LOGIN_URL em settings.py.',
        )

    def test_acesso_negado_ao_painel_sem_staff(self):
        """Valida se usuários autenticados sem staff também são bloqueados do painel administrativo."""
        response = self.cliente_comum.get(self.url_painel)

        self.assertEqual(
            response.status_code,
            302,
            'FALHA: o painel aceitou acesso de um usuário comum. Verifique user_passes_test e is_staff em views.py.',
        )
        self.assertIn(
            '/accounts/login/',
            response.url,
            'FALHA: o usuário comum não foi enviado para a tela de login. Verifique a política de acesso do painel.',
        )

    def test_usuario_comum_nao_exclui_doacao_de_terceiro(self):
        """Previne exclusão indevida de doação por um usuário autenticado sem permissão de staff."""
        doador = Doador.objects.create(
            nome='Joao Doador',
            email='joao@example.com',
            telefone='11999990000',
        )
        doacao = Doacao.objects.create(
            doador=doador,
            nome_item='Jaqueta',
            categoria='Roupa',
            descricao='Jaqueta - Muito nova - tamanho G',
            quantidade=1,
            tipo_entrega='RETIRADA',
            endereco_cep='01001-000',
            endereco_logradouro='Rua Teste',
            endereco_numero='123',
            endereco_complemento='',
            endereco_bairro='Centro',
            endereco_cidade='Sao Paulo',
            endereco_uf='SP',
            status='PENDENTE',
        )
        Agendamento.objects.create(
            doacao=doacao,
            tipo='RETIRADA',
            data=proxima_data_dia_semana(0),
            horario_retirada='10:00',
        )

        response = self.cliente_comum.post(reverse('deletar_doacao', kwargs={'pk': doacao.pk}))

        self.assertEqual(
            response.status_code,
            302,
            'FALHA: a exclusão de doação aceitou um usuário sem staff. Verifique a proteção da rota deletar_doacao.',
        )
        self.assertTrue(
            Doacao.objects.filter(pk=doacao.pk).exists(),
            'FALHA: a doação foi removida por um usuário sem permissão. Confirme se a exclusão está restrita ao staff.',
        )

    def test_usuario_comum_nao_altera_status_de_doacao(self):
        """Previne alteração de status por um usuário autenticado sem staff via URL direta."""
        doador = Doador.objects.create(
            nome='Ana Doadora',
            email='ana@example.com',
            telefone='11911112222',
        )
        doacao = Doacao.objects.create(
            doador=doador,
            nome_item='Calca',
            categoria='Roupa',
            descricao='Calca - nova - tamanho 40',
            quantidade=1,
            tipo_entrega='ENTREGA',
            endereco_cep='',
            endereco_logradouro='',
            endereco_numero='',
            endereco_complemento='',
            endereco_bairro='',
            endereco_cidade='',
            endereco_uf='',
            status='PENDENTE',
        )

        response = self.cliente_comum.post(
            reverse('atualizar_status_doacao', kwargs={'pk': doacao.pk}),
            data={'status': 'CONCLUIDA'},
        )

        self.assertEqual(
            response.status_code,
            302,
            'FALHA: o status da doação aceitou alteração por usuário sem staff. Verifique atualizar_status_doacao.',
        )
        doacao.refresh_from_db()
        self.assertEqual(
            doacao.status,
            'PENDENTE',
            'FALHA: o status da doação mudou indevidamente. Verifique as permissões da rota de atualização.',
        )

    def test_usuario_comum_nao_da_baixa_em_doacao_de_terceiro(self):
        """Previne baixa de estoque por usuário autenticado sem staff na URL direta."""
        doador = Doador.objects.create(
            nome='Carla Doadora',
            email='carla@example.com',
            telefone='11922223333',
        )
        doacao = Doacao.objects.create(
            doador=doador,
            nome_item='Cobertor',
            categoria='Cobertores',
            descricao='Cobertor grosso',
            quantidade=2,
            tipo_entrega='ENTREGA',
            endereco_cep='',
            endereco_logradouro='',
            endereco_numero='',
            endereco_complemento='',
            endereco_bairro='',
            endereco_cidade='',
            endereco_uf='',
            status='CONCLUIDA',
        )

        response = self.cliente_comum.post(reverse('dar_baixa_doacao', kwargs={'pk': doacao.pk}))

        self.assertEqual(
            response.status_code,
            302,
            'FALHA: a baixa de estoque aceitou um usuário sem staff. Verifique a proteção da rota dar_baixa_doacao.',
        )
        doacao.refresh_from_db()
        self.assertEqual(
            doacao.status,
            'CONCLUIDA',
            'FALHA: a baixa foi aplicada sem autorização. A doação deveria permanecer concluída.',
        )

    def test_campo_legado_e_scripts_sao_escapados_no_detalhe(self):
        """Previne regressão de injeção de dados e garante escaping de conteúdo malicioso no HTML."""
        payload = self._payload_retirada(
            nome_item='<script>alert(1)</script>',
            descricao='<img src=x onerror=alert(2)>',
            tamanho='GG',
        )

        response = self.cliente_visitante.post(self.url_cadastrar, data=payload)

        self.assertEqual(
            response.status_code,
            302,
            'FALHA: o cadastro com campo legado ou script malicioso não redirecionou corretamente. Verifique cadastrar_doacao.',
        )
        self.assertTrue(
            response.url.endswith(reverse('doacao_confirmacao')),
            'FALHA: o cadastro não levou para a confirmação. Verifique a rota doacao_confirmacao.',
        )
        doacao = Doacao.objects.get()
        self.assertFalse(
            hasattr(doacao, 'tamanho'),
            'FALHA: o modelo ainda expõe o atributo tamanho. Remova qualquer uso legado desse campo.',
        )

        resposta_detalhe = self.cliente_staff.get(reverse('doacao_detalhe', kwargs={'id': doacao.id}))
        self.assertEqual(
            resposta_detalhe.status_code,
            200,
            'FALHA: a página de detalhes da doação não carregou para staff. Verifique a rota doacao_detalhe.',
        )
        self.assertNotContains(
            resposta_detalhe,
            '<script>alert(1)</script>',
            html=False,
            msg_prefix='FALHA: o script malicioso apareceu sem escape no HTML. Verifique o template de detalhes.',
        )
        self.assertNotContains(
            resposta_detalhe,
            '<img src=x onerror=alert(2)>',
            html=False,
            msg_prefix='FALHA: o payload malicioso apareceu sem escape no HTML. Verifique o template de detalhes.',
        )
        self.assertContains(
            resposta_detalhe,
            '&lt;script&gt;alert(1)&lt;/script&gt;',
            html=False,
            msg_prefix='FALHA: o conteúdo não foi escapado como esperado. Confirme o autoescape do template.',
        )
        self.assertContains(
            resposta_detalhe,
            '&lt;img src=x onerror=alert(2)&gt;',
            html=False,
            msg_prefix='FALHA: o conteúdo não foi escapado como esperado. Confirme o autoescape do template.',
        )

    def test_cadastro_rejeita_cep_invalido_no_backend(self):
        """Previne bypass da validação de CEP quando o frontend envia um formato inválido."""
        payload = self._payload_retirada(cep_retirada='0100100')

        response = self.cliente_visitante.post(self.url_cadastrar, data=payload)

        self.assertEqual(
            response.status_code,
            200,
            'FALHA: o backend aceitou um CEP inválido. Verifique a validação em cadastrar_doacao.',
        )
        self.assertContains(
            response,
            'CEP inválido. Use o formato 00000-000.',
            html=False,
            msg_prefix='FALHA: a mensagem de CEP inválido não apareceu. Verifique o retorno de erro no template.',
        )
        self.assertEqual(
            Doador.objects.count(),
            0,
            'FALHA: um doador foi salvo mesmo com CEP inválido. Verifique o bloco de validação da view.',
        )
        self.assertEqual(
            Doacao.objects.count(),
            0,
            'FALHA: uma doação foi salva mesmo com CEP inválido. Verifique o bloco de validação da view.',
        )
        self.assertEqual(
            Agendamento.objects.count(),
            0,
            'FALHA: um agendamento foi salvo mesmo com CEP inválido. Verifique o bloco de validação da view.',
        )

    def test_cadastro_aceita_horario_coleta_no_formato_hh_mm(self):
        """Previne regressão na sincronização do horário aceito pelo backend."""
        payload = self._payload_retirada(horario_coleta='10:30')

        response = self.cliente_visitante.post(self.url_cadastrar, data=payload)

        self.assertEqual(
            response.status_code,
            302,
            'FALHA: o cadastro com horário válido não redirecionou. Verifique o fluxo de retirada em cadastrar_doacao.',
        )
        doacao = Doacao.objects.get()
        agendamento = Agendamento.objects.get()
        self.assertEqual(
            agendamento.horario_retirada.strftime('%H:%M'),
            '10:30',
            'FALHA: o horário de coleta não foi persistido em HH:MM. Verifique o mapeamento horario_coleta.',
        )
        self.assertEqual(
            agendamento.tipo,
            'RETIRADA',
            'FALHA: o agendamento não foi salvo como RETIRADA. Verifique o tipo gravado na view.',
        )
        self.assertEqual(
            doacao.status,
            'PENDENTE',
            'FALHA: o status padrão da doação não foi preservado. Verifique o fluxo de criação.',
        )

    def test_cadastro_rejeita_horario_coleta_fora_do_padrao(self):
        """Previne persistência de horário malformado no banco de dados."""
        payload = self._payload_retirada(horario_coleta='10:30:15')

        response = self.cliente_visitante.post(self.url_cadastrar, data=payload)

        self.assertEqual(
            response.status_code,
            200,
            'FALHA: o backend aceitou um horário fora do padrão HH:MM. Verifique a conversão do horário de retirada.',
        )
        self.assertContains(
            response,
            'Formato de horário de retirada inválido.',
            html=False,
            msg_prefix='FALHA: a mensagem de horário inválido não apareceu. Verifique o tratamento de exceção.',
        )
        self.assertEqual(
            Doacao.objects.count(),
            0,
            'FALHA: uma doação foi salva mesmo com horário inválido. Verifique o bloco de validação do backend.',
        )
        self.assertEqual(
            Agendamento.objects.count(),
            0,
            'FALHA: um agendamento foi salvo mesmo com horário inválido. Verifique o bloco de validação do backend.',
        )

    def test_fluxo_completo_exibe_dados_corretos_no_painel(self):
        """Previne regressão no fluxo feliz e garante que o painel exiba os dados consolidados corretos."""
        payload = self._payload_retirada(
            nome_item='Cobertor infantil',
            descricao='Quente para o inverno',
            categoria=['Cobertores'],
            quantidade='3',
            data_retirada=proxima_data_dia_semana(2).isoformat(),
            horario_coleta='11:00',
        )

        response = self.cliente_visitante.post(self.url_cadastrar, data=payload)

        self.assertEqual(
            response.status_code,
            302,
            'FALHA: o fluxo completo de cadastro não redirecionou corretamente. Verifique cadastrar_doacao.',
        )
        doacao = Doacao.objects.get()
        self.assertEqual(
            doacao.status,
            'PENDENTE',
            'FALHA: a doação criada no fluxo feliz não ficou com status PENDENTE. Verifique o save inicial.',
        )
        self.assertEqual(
            doacao.descricao,
            'Cobertor infantil - Quente para o inverno',
            'FALHA: a descrição consolidada não foi montada corretamente. Verifique o campo descricao no backend.',
        )

        self.cliente_staff.post(
            reverse('atualizar_status_doacao', kwargs={'pk': doacao.pk}),
            data={'status': 'CONCLUIDA'},
        )

        resposta_painel = self.cliente_staff.get(self.url_painel)
        self.assertEqual(
            resposta_painel.status_code,
            200,
            'FALHA: o painel administrativo não carregou. Verifique a rota admin_dashboard e as permissões de staff.',
        )
        self.assertContains(
            resposta_painel,
            'Cobertor infantil - Quente para o inverno',
            html=False,
            msg_prefix='FALHA: a descrição da doação concluída não apareceu no painel. Verifique o template.',
        )
        self.assertContains(
            resposta_painel,
            'Cobertores',
            html=False,
            msg_prefix='FALHA: a categoria da doação não apareceu no painel. Verifique o resumo de estoque.',
        )
        self.assertContains(
            resposta_painel,
            '3',
            html=False,
            msg_prefix='FALHA: a quantidade da doação não apareceu no painel. Verifique o resumo de estoque.',
        )

    def test_modelo_rejeita_doacao_sem_doador(self):
        """Previne criação de doação sem vínculo com doador no nível do modelo."""
        doacao = Doacao(
            nome_item='Item sem dono',
            categoria='Roupa',
            descricao='Descricao sem doador',
            quantidade=1,
            tipo_entrega='ENTREGA',
            endereco_cep='01001-000',
            endereco_logradouro='Rua Teste',
            endereco_numero='123',
            endereco_complemento='',
            endereco_bairro='Centro',
            endereco_cidade='Sao Paulo',
            endereco_uf='SP',
        )

        with self.assertRaises(ValidationError):
            try:
                doacao.full_clean()
            except ValidationError as erro:
                self.assertIn(
                    'doador',
                    erro.message_dict,
                    'FALHA: a validação não apontou ausência de doador. Verifique o campo obrigatório do modelo.',
                )
                raise

    def test_modelo_rejeita_doacao_sem_descricao(self):
        """Previne criação de doação sem descrição, que é obrigatória no modelo atual."""
        doador = Doador.objects.create(
            nome='Doador Valido',
            email='valido@example.com',
            telefone='11900001111',
        )
        doacao = Doacao(
            doador=doador,
            nome_item='Item sem descricao',
            categoria='Roupa',
            quantidade=1,
            tipo_entrega='ENTREGA',
            endereco_cep='01001-000',
            endereco_logradouro='Rua Teste',
            endereco_numero='123',
            endereco_complemento='',
            endereco_bairro='Centro',
            endereco_cidade='Sao Paulo',
            endereco_uf='SP',
        )

        with self.assertRaises(ValidationError):
            try:
                doacao.full_clean()
            except ValidationError as erro:
                self.assertIn(
                    'descricao',
                    erro.message_dict,
                    'FALHA: a validação não apontou ausência de descrição. Verifique o campo obrigatório do modelo.',
                )
                raise

    def test_modelo_define_status_padrao_pendente(self):
        """Garante que uma doação nova mantenha o status padrão PENDENTE."""
        doador = Doador.objects.create(
            nome='Doador Padrao',
            email='padrao@example.com',
            telefone='11912345678',
        )
        doacao = Doacao(
            doador=doador,
            nome_item='Item valido',
            categoria='Roupa',
            descricao='Descricao valida',
            quantidade=1,
            tipo_entrega='ENTREGA',
            endereco_cep='01001-000',
            endereco_logradouro='Rua Teste',
            endereco_numero='123',
            endereco_complemento='',
            endereco_bairro='Centro',
            endereco_cidade='Sao Paulo',
            endereco_uf='SP',
        )
        doacao.full_clean()

        self.assertEqual(
            doacao.status,
            'PENDENTE',
            'FALHA: o status padrão da doação não é PENDENTE. Verifique o default do campo status no model.',
        )

    def test_fluxo_pendente_permanece_com_status_padrao_no_cadastro_publico(self):
        """Previne regressão em que o cadastro público deixaria de persistir status padrão PENDENTE."""
        response = self.cliente_visitante.post(self.url_cadastrar, data=self._payload_retirada())

        self.assertEqual(
            response.status_code,
            302,
            'FALHA: o cadastro público não redirecionou após salvar. Verifique o fluxo de confirmação.',
        )
        doacao = Doacao.objects.get()
        self.assertEqual(
            doacao.status,
            'PENDENTE',
            'FALHA: o cadastro público não manteve o status PENDENTE. Verifique a criação da doação.',
        )

    def test_staff_pode_concluir_doacao(self):
        """Previne regressão na ação de concluir uma doação pelo painel administrativo."""
        doador = Doador.objects.create(
            nome='Doador Painel',
            email='painel@example.com',
            telefone='11988887777',
        )
        doacao = Doacao.objects.create(
            doador=doador,
            nome_item='Itens de inverno',
            categoria='Cobertores',
            descricao='Itens de inverno para teste',
            quantidade=5,
            tipo_entrega='ENTREGA',
            endereco_cep='',
            endereco_logradouro='',
            endereco_numero='',
            endereco_complemento='',
            endereco_bairro='',
            endereco_cidade='',
            endereco_uf='',
            status='PENDENTE',
        )

        resposta_status = self.cliente_staff.post(
            reverse('atualizar_status_doacao', kwargs={'pk': doacao.pk}),
            data={'status': 'CONCLUIDA'},
        )
        self.assertEqual(
            resposta_status.status_code,
            302,
            'FALHA: o staff não conseguiu concluir a doação. Verifique a rota atualizar_status_doacao.',
        )
        doacao.refresh_from_db()
        self.assertEqual(
            doacao.status,
            'CONCLUIDA',
            'FALHA: o status não foi alterado para CONCLUIDA. Verifique a persistência da ação de staff.',
        )

    def test_staff_pode_dar_baixa_em_doacao_concluida(self):
        """Previne regressão na baixa de estoque executada pelo painel administrativo."""
        doador = Doador.objects.create(
            nome='Doador Baixa',
            email='baixa@example.com',
            telefone='11977776666',
        )
        doacao = Doacao.objects.create(
            doador=doador,
            nome_item='Cobertor',
            categoria='Cobertores',
            descricao='Cobertor grosso',
            quantidade=2,
            tipo_entrega='ENTREGA',
            endereco_cep='',
            endereco_logradouro='',
            endereco_numero='',
            endereco_complemento='',
            endereco_bairro='',
            endereco_cidade='',
            endereco_uf='',
            status='CONCLUIDA',
        )

        resposta_baixa = self.cliente_staff.post(reverse('dar_baixa_doacao', kwargs={'pk': doacao.pk}))
        self.assertEqual(
            resposta_baixa.status_code,
            302,
            'FALHA: o staff não conseguiu dar baixa em uma doação concluída. Verifique a rota dar_baixa_doacao.',
        )
        doacao.refresh_from_db()
        self.assertEqual(
            doacao.status,
            'BAIXADA',
            'FALHA: a doação concluída não foi baixada corretamente. Verifique a persistência da ação de staff.',
        )

    def test_validacao_endereco_retirada_sem_campos_obrigatorios(self):
        """Previne cadastro de retirada sem os campos mínimos de endereço obrigatórios."""
        form = DoacaoForm(
            data={
                'nome_item': 'Vestido',
                'categoria': 'Roupa',
                'tamanho': 'M',
                'descricao': 'Vestido em bom estado',
                'quantidade': 1,
                'tipo_entrega': 'RETIRADA',
                'endereco_cep': '',
                'endereco_logradouro': '',
                'endereco_numero': '',
                'endereco_complemento': '',
                'endereco_bairro': '',
                'endereco_cidade': '',
                'endereco_uf': '',
            }
        )

        self.assertFalse(
            form.is_valid(),
            'FALHA: o formulário de retirada foi considerado válido sem endereço. Verifique a validação condicional do DoacaoForm.',
        )
        self.assertIn(
            'Para retirada, informe os campos obrigatórios de endereço',
            str(form.errors),
            'FALHA: a mensagem de validação de endereço não apareceu. Verifique o clean() do DoacaoForm.',
        )

    def test_rollback_total_quando_agendamento_falha(self):
        """Garante rollback completo quando o agendamento falha depois de criar a doação."""
        payload = self._payload_retirada()
        payload.update(
            {
                'metodo_entrega': 'ENTREGA',
                'data_sugerida': proxima_data_dia_semana(1).isoformat(),
                'horario_sugerido': '20:00',
            }
        )

        with patch('bazar.views.Agendamento.objects.create', side_effect=Exception('Falha simulada')):
            with self.assertRaises(Exception):
                self.cliente_visitante.post(self.url_cadastrar, data=payload)

        self.assertEqual(
            Doador.objects.count(),
            0,
            'FALHA: o rollback não removeu o doador criado antes da falha. Verifique transaction.atomic.',
        )
        self.assertEqual(
            Doacao.objects.count(),
            0,
            'FALHA: o rollback não removeu a doação criada antes da falha. Verifique transaction.atomic.',
        )
        self.assertEqual(
            Agendamento.objects.count(),
            0,
            'FALHA: o rollback não removeu o agendamento após a falha simulada. Verifique transaction.atomic.',
        )
