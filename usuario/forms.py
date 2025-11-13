from django import forms
from .models import PreferenciasPreFiltro, PreenchimentoAutomaticoDeCampos
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError


class PreferenciasPreFiltroModelForm(forms.ModelForm):
    class Meta:
        model = PreferenciasPreFiltro
        fields = [
            'volume', 
            # Campos Foreign Key (Select2)
            'projetos', 'componentes',
        ]
        # 1. Adicionando Widgets para UX
        widgets = {
            # 1.2. Configuração dos Select2 (Adicionando a classe 'select2')
            'projetos': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'componentes': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        }
    # 2. Configurando input_formats para o formato brasileiro
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['projetos'].widget.attrs['data-placeholder'] = "Selecione um ou mais projetos com busca..."
        self.fields['componentes'].widget.attrs['data-placeholder'] = "Selecione um ou mais componentes com busca..."

class PreenchimentoAutomaticoDeCamposModelForm(forms.ModelForm):
    class Meta:
        model = PreenchimentoAutomaticoDeCampos
        fields = [
            'status', 'categoria',
            'tipo', 'volume', 
            'localizacao', 
            'unidade', 'capitulo_secao', 'lote',
            'projeto', 'componente',  
        ]
        # 1. Adicionando Widgets para UX
        widgets = {
            # 1.2. Configuração dos Select2 (Adicionando a classe 'select2')
            'projeto': forms.Select(attrs={'class': 'form-control select2'}),
            'componente': forms.Select(attrs={'class': 'form-control select2'}),
            'status': forms.Select(attrs={'class': 'form-control select2'}),
            'categoria': forms.Select(attrs={'class': 'form-control select2'}),
            'localizacao': forms.Select(attrs={'class': 'form-control select2'}),
            'tipo': forms.Select(attrs={'class': 'form-control select2'}),
        }
    # 2. Configurando input_formats para o formato brasileiro
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['projeto'].widget.attrs['data-placeholder'] = "Selecione um ou mais com busca..."
        self.fields['componente'].widget.attrs['data-placeholder'] = "Selecione um ou mais com busca..."
        self.fields['status'].widget.attrs['data-placeholder'] = "Selecione um ou mais com busca..."
        self.fields['categoria'].widget.attrs['data-placeholder'] = "Selecione um ou mais com busca..."
        self.fields['localizacao'].widget.attrs['data-placeholder'] = "Selecione um ou mais com busca..."
        self.fields['tipo'].widget.attrs['data-placeholder'] = "Selecione um ou mais com busca..."

class UsuarioModelForm(UserCreationForm):
    email = forms.EmailField(max_length=100)

    def clean_email(self):
        email_digitado = self.cleaned_data['email']
        if User.objects.filter(email=email_digitado).exists():
            raise ValidationError('Esse e-mail já está em uso.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UsuarioActivateDeactivateForm(forms.ModelForm):
    # criar aqui o formulário de ativação ou desativação de usuário
    # o grupo Coordenador pode ativar/desativar um usuário
    class Meta:
        model = User
        # Exponha is_active e groups, que são campos importantes 
        # para gerenciamento administrativo.
        fields = ['is_active', 'groups', 'username', 'email'] 
        
        widgets = {
            # O is_active será um simples checkbox
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            # O groups pode ser um MultipleSelect para melhor UX no painel
            'groups': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Opcional: Melhore a UX do campo is_active
        self.fields['is_active'].label = 'Usuário ativo (Permitir login)'
        # Opcional: Adicione um placeholder para o select2 de grupos
        self.fields['groups'].widget.attrs['data-placeholder'] = "Gerenciar grupos do usuário..."