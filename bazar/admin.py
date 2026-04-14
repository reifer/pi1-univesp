from django.contrib import admin
from .models import Doador, Doacao, Agendamento


class AgendamentoInline(admin.StackedInline):
    model = Agendamento
    extra = 0


@admin.register(Doacao)
class DoacaoAdmin(admin.ModelAdmin):
    list_display = ('id', 'doador', 'tipo_entrega', 'status', 'quantidade', 'data_criacao')
    list_filter = ('tipo_entrega', 'status', 'data_criacao')
    search_fields = ('descricao', 'doador__nome', 'doador__email')
    readonly_fields = ('data_criacao',)
    inlines = [AgendamentoInline]
    
    fieldsets = (
        ('Doador', {
            'fields': ('doador',)
        }),
        ('Doação', {
            'fields': ('descricao', 'quantidade', 'tipo_entrega', 'status')
        }),
        ('Auditoria', {
            'fields': ('data_criacao',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Doador)
class DoadorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'data_criacao')
    search_fields = ('nome', 'email', 'telefone')
    readonly_fields = ('data_criacao',)


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('doacao', 'tipo', 'data', 'horario', 'endereco')
    list_filter = ('tipo', 'data')
    search_fields = ('doacao__doador__nome', 'doacao__doador__email', 'endereco')

