from django import forms
from .models import PreferenciasPreFiltro, PreenchimentoAutomaticoDeCampos, PreferenciasColunasTabela
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
        return email_digitado
    
    def save(self, commit=True):
        # Chama o save() do UserCreationForm, que cria a instância do User 
        # (salvando username e passwords).
        user = super().save(commit=False) 
        
        # 1. Obtém o email do formulário e define na instância do usuário.
        #    O campo email existe em self.cleaned_data, mas não foi passado
        #    para o save() do UserCreationForm.
        user.email = self.cleaned_data["email"]
        
        # 2. Se 'commit' for True (padrão), salva as alterações no banco.
        if commit:
            user.save()
        
        # 3. Retorna a instância do usuário.
        return user

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

class PreferenciasColunasTabelaForm(forms.ModelForm):
    """
    Formulário para o usuário editar quais colunas do modelo Ilustracao
    devem ser exibidas na tabela principal.
    """
    class Meta:
        model = PreferenciasColunasTabela
        fields = [
            'exibir_status',
            'exibir_categoria',
            'exibir_localizacao',
            'exibir_volume',
            'exibir_unidade',
            'exibir_capitulo_secao',
            'exibir_pagina',
            'exibir_tipo',
            'exibir_descricao',
            'exibir_observacao_edit_nuc',
            'exibir_lote',
            'exibir_data_liberacao_para_arte',
            'exibir_data_envio_pedido',
            'exibir_data_recebimento_rafe',
            'exibir_data_retorno_rafe',
            'exibir_data_recebimento_finalizada',
            'exibir_classificacao',
            'exibir_credito',
            # 'exibir_ilustrador_resgate',
            'exibir_ilustrador',
            'exibir_ilustrador_ajuste',
            'exibir_observacao_arte',
            'exibir_pagamento',
            'exibir_criado_por',
            'exibir_criado_em',
            'exibir_atualizado_por',
            'exibir_modificado_em',
            'exibir_projeto',
            'exibir_componente'
        ]
        widgets = {
            # O Django automaticamente renderiza BooleanField como CheckboxInput,
            # mas você pode personalizar se desejar.
        }