from django.db import models
from django.contrib.auth.models import User
from planilha.models import Base, Projeto, Componente, Ilustracao


class PreenchimentoAutomaticoDeCampos(Base):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preenchimento_automatico',
        verbose_name='Usuário'
    )
    projeto = models.ForeignKey(
        'planilha.Projeto', 
        verbose_name='Projeto preferido',
        related_name='%(class)s_projeto_preferido', 
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    componente = models.ForeignKey(
        'planilha.Componente',
        verbose_name='Componente preferido',
        related_name='%(class)s_componente_preferido',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    volume = models.PositiveIntegerField(
        verbose_name='Volume preferido',
        blank=True,
        null=True,
    )
    unidade = models.PositiveIntegerField(
        verbose_name='Unidade preferida',
        blank=True,
        null=True,
    )
    capitulo_secao = models.CharField(
        verbose_name='Capítulo ou seção preferida',
        blank=True,
        null=True,
    )
    lote = models.PositiveIntegerField(
        verbose_name='Lote preferido',
        blank=True,
        null=True,
    )
    status = models.CharField( #
        verbose_name='Status',
        max_length=50,
        choices=Ilustracao.StatusChoices.choices,  # Aplica o dropdown na interface
        blank=True,
        null=True,
    )
    categoria = models.CharField( #
        verbose_name='Categoria',
        max_length=50,
        choices=Ilustracao.CategoriaChoices.choices,
        blank=True,
        null=True,
    )
    localizacao = models.CharField( #
        verbose_name='Localização',
        max_length=50,
        choices=Ilustracao.LocalizacaoChoices.choices,
        blank=True,
        null=True,
    )
    tipo = models.CharField( #
        verbose_name='Tipo',
        max_length=50,
        choices=Ilustracao.TipoChoices.choices,
        blank=True,
        null=True,
    )
    class Meta:
        verbose_name = 'Preferência de Pré-Filtro'
        verbose_name_plural = 'Preferências de Pré-Filtro'
        ordering = ['id']

    def __str__(self):
        return f"Preferências #{self.pk} ({self.usuario.username if self.usuario else 'Sem Usuário'})"

class PreferenciasPreFiltro(Base):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preferencias_filtro',
        verbose_name='Usuário'
    )
    projetos = models.ManyToManyField(
        'planilha.Projeto', 
        verbose_name='Projetos preferidos',
        related_name='%(class)s_projetos_preferidos', 
        blank=True,
    )
    componentes = models.ManyToManyField(
        'planilha.Componente',
        verbose_name='Componentes preferidos',
        related_name='%(class)s_componentes_preferidos',
        blank=True,
    )
    volume = models.PositiveIntegerField(
        verbose_name='Volume preferido',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Preferência de Pré-Filtro'
        verbose_name_plural = 'Preferências de Pré-Filtro'
        ordering = ['id']

    def __str__(self):
        return f"Preferências #{self.pk} ({self.usuario.username if self.usuario else 'Sem Usuário'})"
