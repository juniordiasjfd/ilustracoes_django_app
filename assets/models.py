from planilha.models import Base
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
    