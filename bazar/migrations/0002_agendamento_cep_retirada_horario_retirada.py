from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bazar', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='agendamento',
            name='cep_retirada',
            field=models.CharField(blank=True, max_length=9, null=True, verbose_name='CEP de Retirada'),
        ),
        migrations.AddField(
            model_name='agendamento',
            name='horario_retirada',
            field=models.TimeField(blank=True, null=True, verbose_name='Horário de Retirada'),
        ),
    ]
