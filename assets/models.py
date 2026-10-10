from planilha.models import Base
from django.core.validators import RegexValidator
from django.db import models


class Dashboard(Base):
    nome = models.CharField(max_length=150)

    texto_intro = models.TextField(
        "Texto de introdutório",
        blank=True,
        null=True
    )

    embed_url = models.URLField("URL do painel")

    ativo = models.BooleanField(default=True)

    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordem", "nome"]

    def __str__(self):
        return self.nome

class LinksExtrasDaPaginaInicial(Base):
    """Links extras exibidos na página inicial.

    Cadastrados pelo admin; a view index envia só os ativos ao template.
    """
    icone = models.CharField(
        max_length=100,
        default='fa-solid fa-link',
        validators=[
            RegexValidator(
                r'^fa[a-z0-9-]*( fa[a-z0-9-]*)*$',
                'Informe só classes do FontAwesome separadas por espaço (ex.: "fa-solid fa-link").',
            )
        ],
        verbose_name="Ícone",
        help_text='Classes do FontAwesome 6 (ex.: "fa-solid fa-link", "fa-brands fa-trello").',
    )
    titulo = models.CharField(max_length=100, verbose_name="Título")
    url = models.URLField(max_length=500, verbose_name="URL")
    nova_aba = models.BooleanField(default=True, verbose_name="Abrir em nova aba")
    ordem = models.PositiveIntegerField(default=0, verbose_name="Ordem de exibição")

    class Meta:
        verbose_name = "Link extra da página inicial"
        verbose_name_plural = "Links extras da página inicial"
        ordering = ['ordem', 'titulo']

    def __str__(self):
        return self.titulo
