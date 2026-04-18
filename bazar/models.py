from django.db import models


class Doador(models.Model):
    nome = models.CharField(max_length=150, verbose_name="Nome do Doador")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")
    email = models.EmailField(unique=True, verbose_name="E-mail")
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.email})"

    class Meta:
        verbose_name = "Doador"
        verbose_name_plural = "Doadores"
        ordering = ['nome']


class Doacao(models.Model):
    TIPO_ENTREGA_CHOICES = [
        ('RETIRADA', 'Retirada'),
        ('ENTREGA', 'Entrega'),
    ]

    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('AGENDADA', 'Agendada'),
        ('CONCLUIDA', 'Concluída'),
        ('BAIXADA', 'Baixada'),
        ('CANCELADA', 'Cancelada'),
    ]

    doador = models.ForeignKey(Doador, on_delete=models.CASCADE, related_name='doacoes', verbose_name="Doador")
    nome_item = models.CharField(max_length=150, blank=True, null=True, verbose_name="Item")
    categoria = models.CharField(max_length=80, blank=True, null=True, verbose_name="Categoria")
    tamanho = models.CharField(max_length=30, blank=True, null=True, verbose_name="Tamanho")
    descricao = models.TextField(verbose_name="Descrição")
    quantidade = models.PositiveIntegerField(default=1, verbose_name="Quantidade")
    tipo_entrega = models.CharField(max_length=20, choices=TIPO_ENTREGA_CHOICES, default='RETIRADA', verbose_name="Tipo de Entrega")
    endereco_cep = models.CharField(max_length=9, blank=False, null=False, default='', verbose_name="CEP de Retirada")
    endereco_logradouro = models.CharField(max_length=255, blank=False, null=False, default='', verbose_name="Logradouro")
    endereco_numero = models.CharField(max_length=20, blank=False, null=False, default='', verbose_name="Número")
    endereco_complemento = models.CharField(max_length=120, blank=True, null=False, default='', verbose_name="Complemento")
    endereco_bairro = models.CharField(max_length=120, blank=False, null=False, default='', verbose_name="Bairro")
    endereco_cidade = models.CharField(max_length=120, blank=False, null=False, default='', verbose_name="Cidade")
    endereco_uf = models.CharField(max_length=2, blank=False, null=False, default='', verbose_name="UF")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE', verbose_name="Status")
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Doação #{self.pk} - {self.doador.nome}"

    class Meta:
        verbose_name = "Doação"
        verbose_name_plural = "Doações"
        ordering = ['-data_criacao']
        constraints = [
            models.CheckConstraint(
                name='retirada_endereco_obrigatorio',
                condition=(
                    ~models.Q(tipo_entrega='RETIRADA')
                    | (
                        ~models.Q(endereco_cep='')
                        & ~models.Q(endereco_logradouro='')
                        & ~models.Q(endereco_numero='')
                        & ~models.Q(endereco_bairro='')
                        & ~models.Q(endereco_cidade='')
                        & ~models.Q(endereco_uf='')
                    )
                ),
            ),
        ]


class Agendamento(models.Model):
    TIPO_CHOICES = [
        ('RETIRADA', 'Retirada'),
        ('ENTREGA', 'Entrega'),
    ]

    doacao = models.OneToOneField(Doacao, on_delete=models.CASCADE, related_name='agendamento', verbose_name="Doação")
    data = models.DateField(blank=True, null=True, verbose_name="Data")
    horario = models.TimeField(blank=True, null=True, verbose_name="Horário")
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, verbose_name="Tipo")
    horario_retirada = models.TimeField(blank=True, null=True, verbose_name="Horário de Retirada")

    def __str__(self):
        return f"Agendamento da Doação #{self.doacao_id}"

    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"

