from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bazar', '0002_agendamento_cep_retirada_horario_retirada'),
    ]

    operations = [
        migrations.AddField(
            model_name='doacao',
            name='categoria',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='Categoria'),
        ),
        migrations.AddField(
            model_name='doacao',
            name='nome_item',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Item'),
        ),
        migrations.AddField(
            model_name='doacao',
            name='tamanho',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Tamanho'),
        ),
        migrations.AlterField(
            model_name='doacao',
            name='status',
            field=models.CharField(choices=[('PENDENTE', 'Pendente'), ('AGENDADA', 'Agendada'), ('CONCLUIDA', 'Concluída'), ('BAIXADA', 'Baixada'), ('CANCELADA', 'Cancelada')], default='PENDENTE', max_length=20, verbose_name='Status'),
        ),
    ]
