from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse

from .models import Agendamento, Doacao, Doador


def next_weekday(target_weekday):
    """Retorna a próxima data para um dia da semana (0=segunda ... 6=domingo)."""
    today = date.today()
    days_ahead = (target_weekday - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)


class ComprehensiveBazarSecurityAndFlowTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.staff_user = self.User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='password123',
            is_staff=True,
        )
        self.common_user = self.User.objects.create_user(
            username='visitor',
            email='visitor@example.com',
            password='password123',
            is_staff=False,
        )

        self.guest_client = Client()
        self.staff_client = Client()
        self.common_client = Client()
        self.staff_client.force_login(self.staff_user)
        self.common_client.force_login(self.common_user)

        self.painel_url = reverse('admin_dashboard')
        self.cadastrar_url = reverse('cadastrar_doacao')

    def _retirada_payload(self, **overrides):
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
            'data_retirada': next_weekday(0).isoformat(),
            'horario_coleta': '10:00',
        }
        payload.update(overrides)
        return payload

    def test_painel_bloqueia_visitante_nao_autenticado(self):
        """Previne bypass do painel por usuários sem autenticação."""
        response = self.guest_client.get(self.painel_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_painel_bloqueia_usuario_comum_sem_staff(self):
        """Previne bypass do painel por usuários autenticados sem permissão de staff."""
        response = self.common_client.get(self.painel_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_usuario_comum_nao_exclui_doacao_de_terceiro_via_url(self):
        """Previne IDOR em exclusão de doação por usuário autenticado sem staff."""
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
            data=next_weekday(0),
            horario_retirada='10:00',
        )

        response = self.common_client.post(reverse('deletar_doacao', kwargs={'pk': doacao.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Doacao.objects.filter(pk=doacao.pk).exists())

    def test_usuario_comum_nao_altera_status_de_doacao_via_url(self):
        """Previne IDOR em mudança de status por usuário autenticado sem staff."""
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

        response = self.common_client.post(
            reverse('atualizar_status_doacao', kwargs={'pk': doacao.pk}),
            data={'status': 'CONCLUIDA'},
        )

        self.assertEqual(response.status_code, 302)
        doacao.refresh_from_db()
        self.assertEqual(doacao.status, 'PENDENTE')

    def test_usuario_comum_nao_registra_baixa_de_terceiro_via_url(self):
        """Previne IDOR em baixa de estoque por usuário autenticado sem staff."""
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

        response = self.common_client.post(reverse('dar_baixa_doacao', kwargs={'pk': doacao.pk}))

        self.assertEqual(response.status_code, 302)
        doacao.refresh_from_db()
        self.assertEqual(doacao.status, 'CONCLUIDA')

    def test_injecao_de_campos_desconhecidos_e_scripts_sao_escapados_no_painel(self):
        """Previne bypass por campo legado e garante escaping de conteúdo malicioso no HTML."""
        payload = self._retirada_payload(
            nome_item='<script>alert(1)</script>',
            descricao='<img src=x onerror=alert(2)>',
            tamanho='GG',
        )

        response = self.guest_client.post(self.cadastrar_url, data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith(reverse('doacao_confirmacao')))
        doacao = Doacao.objects.get()
        self.assertFalse(hasattr(doacao, 'tamanho'))

        painel_response = self.staff_client.get(reverse('doacao_detalhe', kwargs={'id': doacao.id}))
        self.assertEqual(painel_response.status_code, 200)
        self.assertNotContains(painel_response, '<script>alert(1)</script>', html=False)
        self.assertNotContains(painel_response, '<img src=x onerror=alert(2)>', html=False)
        self.assertContains(painel_response, '&lt;script&gt;alert(1)&lt;/script&gt;', html=False)
        self.assertContains(painel_response, '&lt;img src=x onerror=alert(2)&gt;', html=False)

    def test_cadastro_rejeita_cep_invalido_no_backend(self):
        """Previne bypass de validação de CEP quando o frontend envia um formato inválido."""
        payload = self._retirada_payload(cep_retirada='0100100')

        response = self.guest_client.post(self.cadastrar_url, data=payload)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CEP inválido. Use o formato 00000-000.', html=False)
        self.assertEqual(Doador.objects.count(), 0)
        self.assertEqual(Doacao.objects.count(), 0)
        self.assertEqual(Agendamento.objects.count(), 0)

    def test_cadastro_aceita_horario_coleta_no_formato_hh_mm(self):
        """Previne regressão na sincronização do horário aceito pelo backend."""
        payload = self._retirada_payload(horario_coleta='10:30')

        response = self.guest_client.post(self.cadastrar_url, data=payload)

        self.assertEqual(response.status_code, 302)
        doacao = Doacao.objects.get()
        agendamento = Agendamento.objects.get()
        self.assertEqual(agendamento.horario_retirada.strftime('%H:%M'), '10:30')
        self.assertEqual(agendamento.tipo, 'RETIRADA')
        self.assertEqual(doacao.status, 'PENDENTE')

    def test_cadastro_rejeita_horario_coleta_fora_do_padrão(self):
        """Previne persistência de horário malformado no banco de dados."""
        payload = self._retirada_payload(horario_coleta='10:30:15')

        response = self.guest_client.post(self.cadastrar_url, data=payload)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Formato de horário de retirada inválido.', html=False)
        self.assertEqual(Doacao.objects.count(), 0)
        self.assertEqual(Agendamento.objects.count(), 0)

    def test_fluxo_completo_aparece_no_painel_com_campos_corretos(self):
        """Previne regressão no fluxo feliz e garante que o painel exiba dados consolidados corretos."""
        payload = self._retirada_payload(
            nome_item='Cobertor infantil',
            descricao='Quente para o inverno',
            categoria=['Cobertores'],
            quantidade='3',
            data_retirada=next_weekday(2).isoformat(),
            horario_coleta='11:00',
        )

        response = self.guest_client.post(self.cadastrar_url, data=payload)

        self.assertEqual(response.status_code, 302)
        doacao = Doacao.objects.get()
        self.assertEqual(doacao.status, 'PENDENTE')
        self.assertEqual(doacao.descricao, 'Cobertor infantil - Quente para o inverno')

        self.staff_client.post(reverse('atualizar_status_doacao', kwargs={'pk': doacao.pk}), data={'status': 'CONCLUIDA'})

        painel_response = self.staff_client.get(self.painel_url)
        self.assertEqual(painel_response.status_code, 200)
        self.assertContains(painel_response, 'Cobertor infantil - Quente para o inverno', html=False)
        self.assertContains(painel_response, 'Cobertores', html=False)
        self.assertContains(painel_response, '3', html=False)

    def test_modelo_rejeita_doacao_sem_doador_ou_descricao(self):
        """Previne criação de registros incompletos no nível do modelo e valida o status padrão."""
        doacao_sem_doador = Doacao(
            nome_item='Item sem dono',
            categoria='Roupa',
            descricao='Descrição sem doador',
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
            doacao_sem_doador.full_clean()

        doador = Doador.objects.create(
            nome='Doador Valido',
            email='valido@example.com',
            telefone='11900001111',
        )

        doacao_sem_descricao = Doacao(
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
            doacao_sem_descricao.full_clean()

        doacao_com_status_padrao = Doacao(
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
        doacao_com_status_padrao.full_clean()
        self.assertEqual(doacao_com_status_padrao.status, 'PENDENTE')

    def test_fluxo_pendente_permanece_com_status_padrao_no_cadastro_publico(self):
        """Previne regressão em que o cadastro público deixaria de persistir status padrão PENDENTE."""
        response = self.guest_client.post(self.cadastrar_url, data=self._retirada_payload())

        self.assertEqual(response.status_code, 302)
        doacao = Doacao.objects.get()
        self.assertEqual(doacao.status, 'PENDENTE')

    def test_staff_pode_concluir_e_dar_baixa_em_doacao(self):
        """Previne regressão na cadeia de conclusão e baixa refletida no banco."""
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

        status_response = self.staff_client.post(
            reverse('atualizar_status_doacao', kwargs={'pk': doacao.pk}),
            data={'status': 'CONCLUIDA'},
        )
        self.assertEqual(status_response.status_code, 302)
        doacao.refresh_from_db()
        self.assertEqual(doacao.status, 'CONCLUIDA')

        baixa_response = self.staff_client.post(reverse('dar_baixa_doacao', kwargs={'pk': doacao.pk}))
        self.assertEqual(baixa_response.status_code, 302)
        doacao.refresh_from_db()
        self.assertEqual(doacao.status, 'BAIXADA')
