# ====================================================================
# 1. CONFIGURAÇÃO MANDATÓRIA DO AMBIENTE DJANGO
# ====================================================================
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ilustracoes.settings')
django.setup()

# ====================================================================
# 2. IMPORTAÇÕES DE MODELOS
# ====================================================================
import pandas
from planilha.models import Ilustracao, Ilustrador, Credito, Projeto, Componente

def get_verbose_names(model_class):
    """Retorna uma lista de verbose_names para os campos do modelo."""
    verbose_names = []
    # O atributo '_meta' contém metadados do modelo
    for field in model_class._meta.fields:
        # Cada campo tem um atributo 'verbose_name'
        verbose_names.append(field.verbose_name)
    return verbose_names


get_verbose_names(Ilustracao)






