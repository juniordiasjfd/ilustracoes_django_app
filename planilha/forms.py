from django import forms
from .models import Projeto, Ilustracao, Componente, Ilustrador, Credito
from usuario.models import PreenchimentoAutomaticoDeCampos
from usuario.models import PreferenciasPreFiltro
from django.db.models import Q


class IlustracaoModelForm(forms.ModelForm):
    class Meta:
        model = Ilustracao
        fields = [
            'retranca', 'status', 'categoria', 'tipo', 'volume', 'localizacao', 'unidade',
            'capitulo_secao', 'pagina', 'descricao', 'observacao_edit_nuc', 'lote',
            # Campos de Data/Hora (DatePicker)
            'data_liberacao_para_arte', 'data_envio_pedido', 'data_recebimento_rafe', 
            'data_retorno_rafe', 'data_recebimento_finalizada', 
            # Campos Foreign Key (Select2)
            'ilustrador', 'ilustrador_resgate', 'ilustrador_ajuste', 
            'credito', 
            'classificacao', 'observacao_arte', 'pagamento',
            'projeto', 'componente',
        ]
        # 1. Adicionando Widgets para UX
        widgets = {
            # 1.1. Configuração dos DatePickers (Adicionando a classe 'datepicker')
            'data_liberacao_para_arte': forms.DateInput(
                attrs={'class': 'form-control datepicker', 'autocomplete': 'off', 'placeholder': 'Escolha uma data...'},
                format='%d/%m/%Y', # Formato brasileiro
                
            ),
            'data_envio_pedido': forms.DateInput(
                attrs={'class': 'form-control datepicker', 'autocomplete': 'off','placeholder': 'Escolha uma data...'},
                format='%d/%m/%Y'
            ),
            'data_recebimento_rafe': forms.DateInput(
                attrs={'class': 'form-control datepicker', 'autocomplete': 'off', 'placeholder': 'Escolha uma data...'},
                format='%d/%m/%Y'
            ),
            'data_retorno_rafe': forms.DateInput(
                attrs={'class': 'form-control datepicker', 'autocomplete': 'off', 'placeholder': 'Escolha uma data...'},
                format='%d/%m/%Y'
            ),
            'data_recebimento_finalizada': forms.DateInput(
                attrs={'class': 'form-control datepicker', 'autocomplete': 'off', 'placeholder': 'Escolha uma data...'},
                format='%d/%m/%Y'
            ),
            
            # 1.2. Configuração dos Select2 (Adicionando a classe 'select2')
            'ilustrador': forms.Select(attrs={'class': 'form-control select2'}),
            'ilustrador_resgate': forms.Select(attrs={'class': 'form-control select2'}),
            'ilustrador_ajuste': forms.Select(attrs={'class': 'form-control select2'}),
            'credito': forms.Select(attrs={'class': 'form-control select2'}),
            'projeto': forms.Select(attrs={'class': 'form-control select2'}),
            'componente': forms.Select(attrs={'class': 'form-control select2', 'data-placeholder': 'Selecione o Componente (Obrigatório)'}),
            'categoria': forms.Select(attrs={'class': 'form-control select2', 'data-placeholder': 'Selecione a Categoria (Obrigatório)'}),
            # outros campos
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preencha um número...'}),
            'retranca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Preencha com texto...'}),
            'unidade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preencha um número...'}),
            'capitulo_secao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Preencha...'}),
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preencha um número...'}),
            'pagina': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preencha um número...'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Preencha com texto... (Obrigatório)'}),
            'observacao_edit_nuc': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Preencha com texto...'}),
            'lote': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preencha um número...'}),
            'classificacao': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Preencha um número...'}),
            'observacao_arte': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Preencha com texto...'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # ----------------------------------------------------
        # FORMATOS DE DATA PT-BR E PLACEHOLDERS
        # ----------------------------------------------------

        # Configurando input_formats para o formato brasileiro
        # Define o formato de entrada esperado para os campos DateInput
        date_fields = [
            'data_liberacao_para_arte', 'data_envio_pedido', 'data_recebimento_rafe', 
            'data_retorno_rafe', 'data_recebimento_finalizada'
        ]
        for field_name in date_fields:
            if field_name in self.fields:
                self.fields[field_name].input_formats = ['%d/%m/%Y', '%d/%m/%y']
        # Garante que os campos Select2 iniciem vazios, se não forem obrigatórios
        self.fields['ilustrador'].empty_label = "Selecione um ilustrador..." 
        self.fields['ilustrador_resgate'].empty_label = "Selecione um ilustrador..." 
        self.fields['ilustrador_ajuste'].empty_label = "Selecione um ilustrador..." 
        self.fields['credito'].empty_label = "Selecione um crédito..." 
        self.fields['projeto'].empty_label = "Selecione um projeto..." 
        self.fields['componente'].empty_label = "Selecione um componente..." 

        # ----------------------------------------------------
        # FILTRO PARA DAR COMO OPÇÕES PARA O SELECT DA UX
        # APENAS DADOS ATIVOS
        # ----------------------------------------------------

        # Configuração Padrão: Filtra para mostrar apenas objetos ATIVOS
        self.fields['projeto'].queryset = Projeto.objects.filter(ativo=True)
        self.fields['componente'].queryset = Componente.objects.filter(ativo=True)
        self.fields['credito'].queryset = Credito.objects.filter(ativo=True)
        self.fields['ilustrador'].queryset = Ilustrador.objects.filter(ativo=True)
        self.fields['ilustrador_ajuste'].queryset = Ilustrador.objects.filter(ativo=True)

        # Tratamento de Exceção para EDIÇÃO (Instance Check)
        # Se o formulário está sendo usado para editar (self.instance existe):
        if self.instance and self.instance.pk:
            # --- Projeto ---
            projeto_atual = self.instance.projeto
            if not projeto_atual.ativo:
                self.fields['projeto'].queryset |= Projeto.objects.filter(pk=projeto_atual.pk)
            # --- Componente ---
            componente_atual = self.instance.componente
            if not componente_atual.ativo:
                self.fields['componente'].queryset |= Componente.objects.filter(pk=componente_atual.pk)
            # --- Ilustrador (Criação) ---
            ilustrador_criacao_atual = self.instance.ilustrador
            if ilustrador_criacao_atual and not ilustrador_criacao_atual.ativo:
                self.fields['ilustrador'].queryset |= Ilustrador.objects.filter(pk=ilustrador_criacao_atual.pk)
            # --- Ilustrador (Ajuste) ---
            ilustrador_ajuste_atual = self.instance.ilustrador_ajuste
            if ilustrador_ajuste_atual and not ilustrador_ajuste_atual.ativo:
                self.fields['ilustrador_ajuste'].queryset |= Ilustrador.objects.filter(pk=ilustrador_ajuste_atual.pk)
        
        # ----------------------------------------------------
        # TRATAMENTO PARA FORNECER APENAS OPÇÕES DE 
        # DADOS FAVORITOS
        # ----------------------------------------------------

        # trecho para filtrar os créditos, projetos e componentes favoritos
        # apenas os favoritos serão oferecidos ao usuário
        if self.request and self.request.user.is_authenticated:
            try:
                prefs = self.request.user.preferencias_filtro
                projetos_favoritos = prefs.projetos.all()
                componentes_favoritos = prefs.componentes.all()
                # --- Filtro de Projeto ---
                if projetos_favoritos.exists():
                    self.fields['projeto'].queryset = projetos_favoritos.filter(ativo=True).order_by('nome')
                # --- Filtro de Componente ---
                if componentes_favoritos.exists():
                    self.fields['componente'].queryset = componentes_favoritos.filter(ativo=True).order_by('nome')
                # --- Filtro de Crédito (Dependente do Projeto) ---
                if projetos_favoritos.exists() or componentes_favoritos.exists():
                    creditos_queryset = Credito.objects.filter(ativo=True)
                    if projetos_favoritos.exists():
                        creditos_queryset = creditos_queryset.filter(projetos__in=projetos_favoritos)
                    if componentes_favoritos.exists():
                        creditos_queryset = creditos_queryset.filter(componentes__in=componentes_favoritos)
                    self.fields['credito'].queryset = creditos_queryset.distinct().order_by('nome')
                    # # Filtra Créditos que estão associados (via M2M 'projetos') a qualquer um dos projetos favoritos.
                    # self.fields['credito'].queryset = Credito.objects.filter(
                    #     ativo=True,
                    #     projetos__in=projetos_favoritos,
                    #     # componentes__in=componentes_favoritos
                    # ).distinct().order_by('nome')
            except PreferenciasPreFiltro.DoesNotExist:
                # Se não houver objeto de preferências, mantém os querysets iniciais (Todos Ativos).
                pass 
            
        # TRATAMENTO DE EXCEÇÃO PARA EDIÇÃO (Garante que itens inativos sejam visíveis)
        if self.instance and self.instance.pk:
    
            # ----------------------------------------------------
            # --- Crédito (Utiliza Q object para garantir que o item atual seja sempre visível) ---
            # ----------------------------------------------------
            credito_atual = self.instance.credito
            if credito_atual:
                # Pega o QuerySet atual (pode ser o filtrado por favoritos e ativo=True, e talvez único)
                qs_base = self.fields['credito'].queryset
                
                # Cria uma condição OR: (todos os IDs no qs_base) OU (o ID do crédito atual)
                # Isso garante que o crédito atual esteja na lista, mesmo se for inativo OU não favorito.
                condicao_or = Q(pk__in=qs_base.values_list('pk', flat=True)) | Q(pk=credito_atual.pk)
                
                # Reverte para um QuerySet compatível aplicando o filtro OR e garantindo que seja distinto
                self.fields['credito'].queryset = Credito.objects.filter(condicao_or).distinct()
            
            # ----------------------------------------------------
            # --- Projeto (Reaplicando a correção aqui também para evitar o mesmo erro) ---
            # ----------------------------------------------------
            projeto_atual = self.instance.projeto
            if projeto_atual:
                qs_base = self.fields['projeto'].queryset
                condicao_or = Q(pk__in=qs_base.values_list('pk', flat=True)) | Q(pk=projeto_atual.pk)
                self.fields['projeto'].queryset = Projeto.objects.filter(condicao_or).distinct()

            # ----------------------------------------------------
            # --- Componente (Reaplicando a correção aqui também para evitar o mesmo erro) ---
            # ----------------------------------------------------
            componente_atual = self.instance.componente
            if componente_atual:
                qs_base = self.fields['componente'].queryset
                condicao_or = Q(pk__in=qs_base.values_list('pk', flat=True)) | Q(pk=componente_atual.pk)
                self.fields['componente'].queryset = Componente.objects.filter(condicao_or).distinct()

            # ----------------------------------------------------
            # --- Ilustrador (Criação) ---
            # ----------------------------------------------------
            ilustrador_criacao_atual = self.instance.ilustrador
            if ilustrador_criacao_atual:
                qs_base = self.fields['ilustrador'].queryset
                condicao_or = Q(pk__in=qs_base.values_list('pk', flat=True)) | Q(pk=ilustrador_criacao_atual.pk)
                self.fields['ilustrador'].queryset = Ilustrador.objects.filter(condicao_or).distinct()
                
            # ----------------------------------------------------
            # --- Ilustrador (Ajuste) ---
            # ----------------------------------------------------
            ilustrador_ajuste_atual = self.instance.ilustrador_ajuste
            if ilustrador_ajuste_atual:
                qs_base = self.fields['ilustrador_ajuste'].queryset
                condicao_or = Q(pk__in=qs_base.values_list('pk', flat=True)) | Q(pk=ilustrador_ajuste_atual.pk)
                self.fields['ilustrador_ajuste'].queryset = Ilustrador.objects.filter(condicao_or).distinct()

        # ----------------------------------------------------
        # Preenchimento Automático (Apenas para CRIAÇÃO)
        # COM BASE NA OPÇÃO AUTOMATIZAR DA INTERFACE
        # ----------------------------------------------------

        if not self.instance.pk and self.request and self.request.user.is_authenticated:
            try:
                # Tenta obter as preferências do usuário logado
                preferencias_auto = PreenchimentoAutomaticoDeCampos.objects.get(
                    usuario=self.request.user
                )
                # Mapeia os campos do objeto de preferência para os valores iniciais do formulário
                initial_data = {}
                if preferencias_auto.projeto:
                    initial_data['projeto'] = preferencias_auto.projeto
                if preferencias_auto.componente:
                    initial_data['componente'] = preferencias_auto.componente
                if preferencias_auto.volume is not None:
                    initial_data['volume'] = preferencias_auto.volume
                if preferencias_auto.unidade is not None:
                    initial_data['unidade'] = preferencias_auto.unidade
                if preferencias_auto.capitulo_secao:
                    initial_data['capitulo_secao'] = preferencias_auto.capitulo_secao
                if preferencias_auto.lote is not None:
                    initial_data['lote'] = preferencias_auto.lote
                if preferencias_auto.status:
                    initial_data['status'] = preferencias_auto.status
                if preferencias_auto.categoria:
                    initial_data['categoria'] = preferencias_auto.categoria
                if preferencias_auto.localizacao:
                    initial_data['localizacao'] = preferencias_auto.localizacao
                if preferencias_auto.tipo:
                    initial_data['tipo'] = preferencias_auto.tipo
                # Aplica os valores iniciais ao formulário
                self.initial.update(initial_data)
            except PreenchimentoAutomaticoDeCampos.DoesNotExist:
                # O usuário não tem preferências salvas, não faz nada
                pass

    # ----------------------------------------------------
    # Lógica de Ativação/Inativação de uma ilustração
    # ----------------------------------------------------
    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.status == Ilustracao.StatusChoices.EXCLUIDA:
            instance.ativo = False
        else:
            instance.ativo = True
        if commit:
            instance.save()
        return instance
    
class IlustradorModelForm(forms.ModelForm):
    class Meta:
        model = Ilustrador
        fields = [
            'nome', 'sigla', 
            # 'credito', 
            'email', 'telefone'
        ]

class CreditoModelForm(forms.ModelForm):
    class Meta:
        model = Credito
        fields = ['nome', 'projetos', 'componentes']
        widgets = {
            'projetos': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
            'componentes': forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        }

class ComponenteModelForm(forms.ModelForm):
    class Meta:
        model = Componente
        fields = ['nome']

class ProjetoModelForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = ['nome', 'editora', 'ciclo']

class UploadExcelForm(forms.Form):
    arquivo_excel = forms.FileField(
        label='Arquivo Excel (XLSX)',
        help_text='Use a planilha exportada e altere apenas as colunas desejadas. Mantenha a coluna pk.',
        widget=forms.ClearableFileInput(attrs={'accept': '.xlsx'})
    )