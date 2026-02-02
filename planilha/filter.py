import django_filters
from django import forms
from .models import Ilustracao


class IlustracaoFilter(django_filters.FilterSet):
    projeto = django_filters.CharFilter(
        lookup_expr='iregex', 
        field_name='projeto__nome',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Projeto'
    )
    componente = django_filters.CharFilter(
        lookup_expr='iregex', 
        field_name='componente__nome',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Componente'
    )
    retranca = django_filters.CharFilter(
        lookup_expr='iregex', 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Retranca'
    )
    status = django_filters.MultipleChoiceFilter(
        choices=Ilustracao.StatusChoices.choices,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label='Status',
        help_text='Use Ctrl para selecionar dois ou mais.'
    )
    volume = django_filters.NumberFilter(
        lookup_expr='exact',
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Volume'
    )
    unidade = django_filters.NumberFilter(
        lookup_expr='exact',
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Unidade'
    )
    capitulo_secao = django_filters.CharFilter(
        lookup_expr='iregex', 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Capítulo ou seção'
    )
    descricao = django_filters.CharFilter(
        lookup_expr='iregex', 
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Descrição'
    )
    classificacao = django_filters.NumberFilter(
        lookup_expr='exact',
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Classificação'
    )
    credito = django_filters.CharFilter(
        lookup_expr='iregex', 
        field_name='credito__nome',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Crédito'
    )
    pagamento = django_filters.MultipleChoiceFilter(
        choices=Ilustracao.PagamentoChoices.choices,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label='Pagamento',
        help_text='Use Ctrl para selecionar dois ou mais.'
    )
    categoria = django_filters.MultipleChoiceFilter(
        choices=Ilustracao.CategoriaChoices.choices,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label='Categoria',
        help_text='Use Ctrl para selecionar dois ou mais.'
    )
    tipo = django_filters.MultipleChoiceFilter(
        choices=Ilustracao.TipoChoices.choices,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        label='Tipo',
        help_text='Use Ctrl para selecionar dois ou mais.'
    )
    # lote = django_filters.NumberFilter(
    #     lookup_expr='exact',
    #     widget=forms.NumberInput(attrs={'class': 'form-control'}),
    #     label='Lote'
    # )
    # lote_preenchido = django_filters.BooleanFilter(
    #     method='filter_lote_preenchido',
    #     widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    #     label='Lote preenchido'
    # )
    def filter_lote_preenchido(self, queryset, name, value):
        """Filtra apenas Ilustrações onde o campo lote NÃO é nulo."""
        if value:
            # value é True: filtrar lotes NÃO nulos
            return queryset.exclude(lote__isnull=True)
        # value é False (ou None/não selecionado): não aplicar filtro adicional
        # Se você quiser filtrar APENAS lotes nulos quando False, altere a lógica.
        # Por padrão, False ou não marcado não filtra.
        return queryset
    class Meta:
        model = Ilustracao
        # Removemos fields pois definimos todos explicitamente acima
        fields = []

