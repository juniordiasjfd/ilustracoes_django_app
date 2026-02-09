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

class TipoIlustracao(models.Model):
    # Usamos os mesmos choices do modelo original
    nome = models.CharField(
        max_length=50, 
        choices=Ilustracao.TipoChoices.choices, 
        unique=True
    )
    class Meta:
        verbose_name = 'Tipo de Ilustração'
        verbose_name_plural = 'Tipos de Ilustração'
    def __str__(self):
        return self.get_nome_display()
    
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
    tipos = models.ManyToManyField(
        TipoIlustracao,
        verbose_name='Tipos preferidos',
        related_name='%(class)s_tipos_preferidos',
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

class PreferenciasColunasTabela(Base):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='preferencias_colunas',
        verbose_name='Usuário'
    )
    # exibir_retranca = models.BooleanField('Retranca', default=True)
    exibir_status = models.BooleanField('Status', default=True)
    exibir_categoria = models.BooleanField('Categoria', default=True)
    exibir_localizacao = models.BooleanField('Localização', default=True)
    exibir_volume = models.BooleanField('Volume', default=True)
    exibir_unidade = models.BooleanField('Unidade', default=True)
    exibir_capitulo_secao = models.BooleanField('Capítulo/Seção', default=True)
    exibir_pagina = models.BooleanField('Página', default=True)
    exibir_tipo = models.BooleanField('Tipo', default=True)
    exibir_descricao = models.BooleanField('Descrição', default=True)
    exibir_observacao_edit_nuc = models.BooleanField('Observação editorial e núcleo', default=True)
    exibir_lote = models.BooleanField('Lote', default=False)
    exibir_data_liberacao_para_arte = models.BooleanField('Data de liberação para arte', default=True)
    exibir_data_envio_pedido = models.BooleanField('Data de envio do pedido', default=True)
    exibir_data_recebimento_rafe = models.BooleanField('Data de recebimento do rafe', default=True)
    exibir_data_retorno_rafe = models.BooleanField('Data de retorno do rafe', default=True)
    exibir_data_recebimento_finalizada = models.BooleanField('Data de recebimento da finalizada', default=True)
    exibir_classificacao = models.BooleanField('Classificação', default=True)
    exibir_credito = models.BooleanField('Crédito', default=True)
    # exibir_ilustrador_resgate = models.BooleanField('Ilustrador resgate', default=True)
    exibir_ilustrador = models.BooleanField('Ilustrador criação', default=True)
    exibir_ilustrador_ajuste = models.BooleanField('Ilustrador ajuste', default=True)
    exibir_observacao_arte = models.BooleanField('Observação da arte', default=True)
    exibir_pagamento = models.BooleanField('Pagamento', default=True)
    exibir_criado_por = models.BooleanField('Criado por', default=True)
    exibir_criado_em = models.BooleanField('Criado em', default=True)
    exibir_atualizado_por = models.BooleanField('Modificado por', default=True)
    exibir_modificado_em = models.BooleanField('Modificado em', default=True)
    exibir_projeto = models.BooleanField('Projeto', default=True)
    exibir_componente = models.BooleanField('Componente', default=True)

    class Meta:
        verbose_name = 'Preferência de colunas da tabela'
        verbose_name_plural = 'Preferências de colunas da tabela'
        ordering = ['id']

    def __str__(self):
        return f"Colunas #{self.pk} ({self.usuario.username})"