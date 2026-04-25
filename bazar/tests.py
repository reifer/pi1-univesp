from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .forms import DoacaoForm
from .models import Agendamento, Doacao, Doador


def next_weekday(target_weekday):
    """Retorna a próxima data para um dia da semana (0=segunda ... 6=domingo)."""
    today = date.today()
    days_ahead = (target_weekday - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)


class BazarRefactorPhaseFiveTests(TestCase):
    def setUp(self):
        self.doar_url = reverse('cadastrar_doacao')

    def _base_payload(self):
        return {
            'nome_doador': 'Maria Silva',
            'email_doador': 'maria@example.com',
            'telefone_doador': '(11) 98888-7777',
            'nome_item': 'Camiseta',
            'categoria': ['Roupa'],
            'tamanho_item': 'M',
            'descricao': 'Em bom estado',
            'quantidade': '2',
        }

    def test_privacidade_nao_autenticado_nao_ve_dados_sensiveis(self):
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

        response = self.client.get(reverse('doacao_detalhe', kwargs={'id': doacao.id}))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_privacidade_nao_autenticado_recebe_404_para_doacao_nao_publica(self):
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
            status='CONCLUIDA',
        )

        response = self.client.get(reverse('doacao_detalhe', kwargs={'id': doacao.id}))

        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_atomicidade_rollback_quando_agendamento_falha(self):
        payload = self._base_payload()
        payload.update(
            {
                'metodo_entrega': 'ENTREGA',
                'data_sugerida': next_weekday(1).isoformat(),
                'horario_sugerido': '20:00',
            }
        )

        with patch('bazar.views.Agendamento.objects.create', side_effect=Exception('Falha simulada')):
            with self.assertRaises(Exception):
                self.client.post(self.doar_url, data=payload)

        self.assertEqual(Doador.objects.count(), 0)
        self.assertEqual(Doacao.objects.count(), 0)
        self.assertEqual(Agendamento.objects.count(), 0)

    def test_validacao_endereco_retirada_sem_campos_obrigatorios(self):
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

        self.assertFalse(form.is_valid())
        self.assertIn('Para retirada, informe os campos obrigatórios de endereço', str(form.errors))

    def test_fluxo_completo_cadastro_cria_doador_doacao_e_agendamento(self):
        payload = self._base_payload()
        payload.update(
            {
                'metodo_entrega': 'RETIRADA',
                'cep_retirada': '01001-000',
                'endereco_retirada': 'Rua das Flores',
                'numero_retirada': '120',
                'complemento_retirada': 'Casa',
                'bairro_retirada': 'Centro',
                'cidade_retirada': 'Sao Paulo',
                'uf_retirada': 'SP',
                'data_retirada': next_weekday(0).isoformat(),
                'horario_retirada': '10:00',
            }
        )

        response = self.client.post(self.doar_url, data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('doacao_confirmacao'))
        self.assertEqual(Doador.objects.count(), 1)
        self.assertEqual(Doacao.objects.count(), 1)
        self.assertEqual(Agendamento.objects.count(), 1)

        doador = Doador.objects.first()
        doacao = Doacao.objects.first()
        agendamento = Agendamento.objects.first()

        self.assertEqual(doacao.doador, doador)
        self.assertEqual(agendamento.doacao, doacao)
        self.assertEqual(doacao.tipo_entrega, 'RETIRADA')
        self.assertEqual(agendamento.tipo, 'RETIRADA')
        self.assertEqual(doacao.endereco_cep, '01001-000')
        self.assertEqual(doacao.endereco_logradouro, 'Rua das Flores')
