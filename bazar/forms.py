from django import forms

from .models import Doacao, Doador


class DoadorForm(forms.ModelForm):
    class Meta:
        model = Doador
        fields = ['nome', 'email', 'telefone']

    def clean_nome(self):
        return (self.cleaned_data.get('nome') or '').strip()

    def clean_email(self):
        return (self.cleaned_data.get('email') or '').strip().lower()

    def clean_telefone(self):
        telefone = (self.cleaned_data.get('telefone') or '').strip()
        import re
        telefone = re.sub(r'\D', '', telefone)
        return telefone or None


class DoacaoForm(forms.ModelForm):
    class Meta:
        model = Doacao
        fields = [
            'nome_item',
            'categoria',
            'tamanho',
            'descricao',
            'quantidade',
            'tipo_entrega',
            'endereco_cep',
            'endereco_logradouro',
            'endereco_numero',
            'endereco_complemento',
            'endereco_bairro',
            'endereco_cidade',
            'endereco_uf',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # A obrigatoriedade de endereço é validada de forma condicional para RETIRADA.
        for field_name in [
            'endereco_cep',
            'endereco_logradouro',
            'endereco_numero',
            'endereco_complemento',
            'endereco_bairro',
            'endereco_cidade',
            'endereco_uf',
        ]:
            self.fields[field_name].required = False

    def clean_nome_item(self):
        nome_item = (self.cleaned_data.get('nome_item') or '').strip()
        return nome_item or None

    def clean_categoria(self):
        categoria = (self.cleaned_data.get('categoria') or '').strip()
        return categoria or None

    def clean_tamanho(self):
        tamanho = (self.cleaned_data.get('tamanho') or '').strip()
        return tamanho or None

    def clean_descricao(self):
        return (self.cleaned_data.get('descricao') or '').strip()

    def clean_endereco_cep(self):
        cep = (self.cleaned_data.get('endereco_cep') or '').strip()
        return cep

    def clean_endereco_logradouro(self):
        logradouro = (self.cleaned_data.get('endereco_logradouro') or '').strip()
        return logradouro

    def clean_endereco_numero(self):
        numero = (self.cleaned_data.get('endereco_numero') or '').strip()
        return numero

    def clean_endereco_complemento(self):
        complemento = (self.cleaned_data.get('endereco_complemento') or '').strip()
        return complemento

    def clean_endereco_bairro(self):
        bairro = (self.cleaned_data.get('endereco_bairro') or '').strip()
        return bairro

    def clean_endereco_cidade(self):
        cidade = (self.cleaned_data.get('endereco_cidade') or '').strip()
        return cidade

    def clean_endereco_uf(self):
        uf = (self.cleaned_data.get('endereco_uf') or '').strip().upper()
        return uf

    def clean_quantidade(self):
        quantidade = self.cleaned_data.get('quantidade')
        return max(1, quantidade or 1)

    def clean(self):
        cleaned_data = super().clean()
        tipo_entrega = cleaned_data.get('tipo_entrega')

        if tipo_entrega == 'RETIRADA':
            required_address_fields = {
                'endereco_cep': 'CEP',
                'endereco_logradouro': 'logradouro',
                'endereco_numero': 'número',
                'endereco_bairro': 'bairro',
                'endereco_cidade': 'cidade',
                'endereco_uf': 'UF',
            }
            missing = [label for field, label in required_address_fields.items() if not (cleaned_data.get(field) or '').strip()]
            if missing:
                raise forms.ValidationError(
                    f"Para retirada, informe os campos obrigatórios de endereço: {', '.join(missing)}."
                )

        return cleaned_data
