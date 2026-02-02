from django.db import models
from django.conf import settings
from planilha.middleware import get_current_user
from django.utils import timezone


class Base(models.Model):
    criado_em = models.DateTimeField('Criado em', auto_now_add=True)
    modificado_em = models.DateTimeField('Modificado em', auto_now=True)
    ativo = models.BooleanField('Ativo', default=True)
    # Novos campos de Foreign Key para o Usuário
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Criado por',
        on_delete=models.SET_NULL,  # Se o usuário for deletado, o campo fica NULL
        null=True,
        blank=True,
        related_name='%(class)s_criados'  # Evita conflito de related_name
    )
    atualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name='Atualizado por',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_atualizados'  # Evita conflito de related_name
    )
    def save(self, *args, **kwargs):
        user = get_current_user()
        if not self.pk and not self.criado_por:
            self.criado_por = user
        self.atualizado_por = user
        super().save(*args, **kwargs)
    class Meta:
        abstract = True

class Ilustrador(Base):
    nome = models.CharField('Nome do ilustrador', max_length=150, unique=True)
    sigla = models.CharField('Sigla do ilustrador', max_length=20, unique=True)
    # credito = models.CharField('Crédito do ilustrador', max_length=150)
    email = models.EmailField('E-mail de contato', max_length=150, null=True, blank=True)
    telefone = models.CharField('Telefone do contato', max_length=20, null=True, blank=True)
    class Meta:
        verbose_name = 'Ilustrador'
        verbose_name_plural = 'Ilustradores'
        ordering = ['nome']
    def __str__(self):
        return f"{self.sigla} - {self.nome}"

class Credito(Base):
    nome = models.CharField('Crédito', max_length=100, unique=True)
    projetos = models.ManyToManyField(
        'Projeto', 
        verbose_name='Projetos associados',
        related_name='creditos_projetos_associados', 
        # null=True,
        blank=True,
    )
    componentes = models.ManyToManyField(
        'Componente',
        verbose_name='Componentes associados',
        related_name='creditos_componentes_associados',
        # null=True,
        blank=True,
    )
    class Meta:
        verbose_name = 'Crédito'
        verbose_name_plural = 'Créditos'
        ordering = ['nome']
    def __str__(self):
        return self.nome

class Ilustracao(Base):
    # 1. Definição das escolhas (Como uma classe aninhada para melhor organização)
    class StatusChoices(models.TextChoices):
        # Valor a ser salvo no DB, Display Name na interface
        EDICAO_EQUIPE = 'EDICAO_EQUIPE', 'EDICAO_EQUIPE'
        EDICAO_ARTE = 'EDICAO_ARTE', 'EDICAO_ARTE'
        ILUSTRANDO = 'ILUSTRANDO', 'ILUSTRANDO'
        AVALIANDO = 'AVALIANDO', 'AVALIANDO'
        AJUSTANDO = 'AJUSTANDO', 'AJUSTANDO'
        FINALIZANDO = 'FINALIZANDO', 'FINALIZANDO'
        PRONTA = 'PRONTA', 'PRONTA'
        APLICADA = 'APLICADA', 'APLICADA'
        EXCLUIDA = 'EXCLUÍDA', 'EXCLUÍDA'
    class CategoriaChoices(models.TextChoices):
        ILUSTRACAO = 'ILUSTRAÇÃO', 'ILUSTRAÇÃO'
        IL_FOTO = 'IL + FOTO', 'IL + FOTO'
        GRAFICO = 'GRÁFICO', 'GRÁFICO'
        GRAF_TEC = 'GRÁFICO TÉC', 'GRÁFICO TÉC'
        MAPA = 'MAPA', 'MAPA'
        LINHA_TEMPO = 'LINHA TEMPO', 'LINHA TEMPO'
        INFOGRAFICO = 'INFOGRÁFICO', 'INFOGRÁFICO'
        IL_TEC_ARTE = 'IL TÉC ARTE', 'IL TÉC ARTE'
        IL_TEC_PADRAO = 'IL TÉC PADRÃO', 'IL TÉC PADRÃO'
        IL_TEC_MAT = 'IL TÉC MAT', 'IL TÉC MAT'
    class LocalizacaoChoices(models.TextChoices):
        MIOLO = 'MIOLO', 'MIOLO'
        CAPA = 'CAPA', 'CAPA'
        APRESENT = 'APRESENT', 'APRESENT'
        SUMARIO = 'SUMÁRIO', 'SUMÁRIO'
        ABERTURA = 'ABERTURA', 'ABERTURA'
        PAG_ESPECIAL = 'PÁG ESPECIAL', 'PAG ESPECIAL'
        MP_G = 'MP-G', 'MP-G'
        MP_E = 'MP-E', 'MP-E'
        OED = 'OED', 'OED'
    class TipoChoices(models.TextChoices):
        AJUSTE = 'AJUSTE', 'AJUSTE'
        NOVA = 'NOVA', 'NOVA'
        RESGATE = 'RESGATE', 'RESGATE'
    class PagamentoChoices(models.TextChoices):
        AVALIAR = 'AVALIAR', 'AVALIAR'
        PREVISAO =  'PREVISÃO', 'PREVISÃO'
        FINALIZADO = 'FINALIZADO', 'FINALIZADO'
        FINALIZADO_RAFE = 'FINALIZADO RAFE', 'FINALIZADO RAFE'
        PAGO = 'PAGO', 'PAGO'
        PAGO_RAFE = 'PAGO RAFE', 'PAGO RAFE'
        SEM_PAGAMNTO = 'SEM PAGAMENTO', 'SEM PAGAMENTO'
    retranca = models.CharField('Retranca', max_length=100, unique=True) #
    descricao = models.TextField('Descrição', max_length=2000) #
    volume = models.PositiveIntegerField('Volume', null=False, blank=False) #
    pagina = models.PositiveIntegerField('Página', null=True, blank=True) #
    unidade = models.PositiveIntegerField('Unidade', null=True, blank=True) #
    capitulo_secao = models.CharField('Capítulo ou seção', max_length=100, null=True, blank=True) #
    observacao_edit_nuc = models.TextField('Observação editorial e núcleo', null=True, blank=True, max_length=2000)
    lote = models.PositiveIntegerField('Lote', null=True, blank=True, default=0)
    data_liberacao_para_arte = models.DateTimeField('Data de liberação do lote', null=True, blank=True, default=timezone.now)
    data_envio_pedido = models.DateTimeField('Data de envio do pedido', null=True, blank=True)
    data_recebimento_rafe = models.DateTimeField('Data de recebimento do rafe', null=True, blank=True)
    data_retorno_rafe = models.DateTimeField('Data de retorno do rafe', null=True, blank=True)
    data_recebimento_finalizada = models.DateTimeField('Data de recebimento da finalizada', null=True, blank=True)
    classificacao = models.PositiveIntegerField('Classificação', null=True, blank=True)
    observacao_arte = models.TextField('Observação arte', null=True, blank=True, max_length=2000)
    # 2. Declaração do campo que será persistido no banco
    status = models.CharField( #
        verbose_name='Status',
        max_length=50,  # Garante espaço suficiente para o valor mais longo (10 caracteres para 'ILUSTRANDO')
        choices=StatusChoices.choices,  # Aplica o dropdown na interface
        # default=StatusChoices.EDICAO_EQUIPE  # Define um valor padrão
        null=False,
        blank=False,
    )
    categoria = models.CharField( #
        verbose_name='Categoria',
        max_length=50,
        choices=CategoriaChoices.choices,
        # default=CategoriaChoices.ILUSTRACAO,
        null=False,
        blank=False,
    )
    localizacao = models.CharField( #
        verbose_name='Localização',
        max_length=50,
        choices=LocalizacaoChoices.choices,
        # default=LocalizacaoChoices.MIOLO,
        null=False,
        blank=False,
    )
    tipo = models.CharField( #
        verbose_name='Tipo',
        max_length=50,
        choices=TipoChoices.choices,
        # default=TipoChoices.NOVA
        null=False,
        blank=False,
    )
    pagamento = models.CharField(
        verbose_name='Pagamento',
        max_length=50,
        choices=PagamentoChoices.choices,
        default=PagamentoChoices.AVALIAR,
        null=False,
        blank=False,
    )
    ilustrador = models.ForeignKey(
        'Ilustrador',  # Aponta para o modelo Ilustrador que criamos
        verbose_name='Ilustrador criação',
        on_delete=models.SET_NULL,  # Se o Ilustrador for deletado, o campo fica NULL
        null=True,  # Permite que o campo seja NULL no banco de dados
        blank=True,  # Permite que o campo não seja obrigatório no formulário
        related_name='ilustracoes_criadas'  # Nome para consultas reversas
    )
    # ilustrador_resgate = models.ForeignKey(
    #     'Ilustrador',  # Aponta para o modelo Ilustrador que criamos
    #     verbose_name='Ilustrador resgate',
    #     on_delete=models.SET_NULL,  # Se o Ilustrador for deletado, o campo fica NULL
    #     null=True,  # Permite que o campo seja NULL no banco de dados
    #     blank=True,  # Permite que o campo não seja obrigatório no formulário
    #     related_name='ilustracoes_resgatadas'  # Nome para consultas reversas
    # )
    ilustrador_ajuste = models.ForeignKey(
        'Ilustrador',  # Aponta para o modelo Ilustrador que criamos
        verbose_name='Ilustrador ajuste',
        on_delete=models.SET_NULL,  # Se o Ilustrador for deletado, o campo fica NULL
        null=True,  # Permite que o campo seja NULL no banco de dados
        blank=True,  # Permite que o campo não seja obrigatório no formulário
        related_name='ilustracoes_ajustadas'  # Nome para consultas reversas
    )
    credito = models.ForeignKey(
        'Credito',  # Aponta para o modelo Ilustrador que criamos
        verbose_name='Crédito',
        on_delete=models.SET_NULL,  # Se o Ilustrador for deletado, o campo fica NULL
        null=True,  # Permite que o campo seja NULL no banco de dados
        blank=True,  # Permite que o campo não seja obrigatório no formulário
        related_name='ilustracoes_creditos_associados'  # Nome para consultas reversas
    )
    projeto = models.ForeignKey(
        'Projeto',  # Aponta para o modelo Ilustrador que criamos
        verbose_name='Projeto',
        on_delete=models.PROTECT,  # não permite deletar o projeto
        null=False,  # Não Permite que o campo seja NULL no banco de dados
        blank=False,  # Não Permite que o campo não seja obrigatório no formulário
        related_name='ilustracoes_projetos_associados'  # Nome para consultas reversas
    )
    componente = models.ForeignKey(
        'Componente',  # Aponta para o modelo Ilustrador que criamos
        verbose_name='Componente',
        on_delete=models.PROTECT,  # não permite deletar o componente
        null=False,  # Não Permite que o campo seja NULL no banco de dados
        blank=False,  # Não Permite que o campo não seja obrigatório no formulário
        related_name='ilustracoes_componentes_associados'  # Nome para consultas reversas
    )
    class Meta:
        ordering = ['retranca']
    def __str__(self):
        return self.retranca


class Componente(Base):
    nome = models.CharField('Componente', max_length=100, unique=True)
    class Meta:
        ordering = ['nome']
    def __str__(self):
        return self.nome


class Projeto(Base):
    nome = models.CharField('Projeto', max_length=100, unique=True)
    editora = models.CharField('Editora', max_length=100)
    ciclo = models.CharField('Ciclo', max_length=100)
    class Meta:
        ordering = ['nome']
    def __str__(self):
        return self.nome




