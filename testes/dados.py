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
import datetime


dados_ilustradores = pandas.read_excel('testes/dados.xlsx', 'CRÉDITOS_GERAIS')
for i in dados_ilustradores.index:
    '''
    i=0
    '''
    pessoa = Ilustrador()
    pessoa.nome = dados_ilustradores.iloc[i]['nome']
    pessoa.sigla = dados_ilustradores.iloc[i]['sigla']
    pessoa.credito = dados_ilustradores.iloc[i]['credito']
    pessoa.criado_em = datetime.datetime.now()
    pessoa.modificado_em = datetime.datetime.now()
    pessoa.save()



def get_artista(nome_ilustrador):
    try:
        ilustrador_obj = Ilustrador.objects.get(nome=nome_ilustrador)
    except Ilustrador.DoesNotExist:
        ilustrador_obj = None
    return ilustrador_obj
def get_none(text):
    if text == '':
        return None
    else:
        return text
def clean_date_value(date_value):
    # Verifica se o valor é NaT (Not a Time/Date) ou NaN (Not a Number)
    # que o pandas usa para representar valores ausentes em colunas de data.
    if pandas.isnull(date_value):
        return None
    return date_value
dados = pandas.read_excel('testes/dados.xlsx')
dados = dados.fillna('')
for i in dados.index:
    nova_il = Ilustracao()
    nova_il.retranca = dados.iloc[i]['retranca']
    nova_il.status = dados.iloc[i]['status']
    nova_il.categoria = dados.iloc[i]['categoria']
    nova_il.localizacao = dados.iloc[i]['localizacao']
    nova_il.pagina = get_none(dados.iloc[i]['pagina'])
    nova_il.volume = get_none(dados.iloc[i]['volume'])
    nova_il.unidade = get_none(dados.iloc[i]['unidade'])
    nova_il.capitulo_secao = dados.iloc[i]['capitulo_secao']
    nova_il.tipo = dados.iloc[i]['tipo']
    nova_il.descricao = dados.iloc[i]['descricao']
    nova_il.ilustrador_resgate = get_artista(dados.iloc[i]['ilustrador_resgate'])
    nova_il.observacao_edit_nuc = dados.iloc[i]['observacao_edit_nuc']
    nova_il.lote = get_none(dados.iloc[i]['lote'])
    nova_il.data_liberacao_para_arte = clean_date_value(dados.iloc[i]['data_liberacao_para_arte'])
    nova_il.data_envio_pedido = clean_date_value(dados.iloc[i]['data_envio_pedido'])
    nova_il.data_recebimento_rafe = clean_date_value(dados.iloc[i]['data_recebimento_rafe'])
    nova_il.data_retorno_rafe = clean_date_value(dados.iloc[i]['data_retorno_rafe'])
    nova_il.data_recebimento_finalizada = clean_date_value(dados.iloc[i]['data_recebimento_finalizada'])
    nova_il.ilustrador = get_artista(dados.iloc[i]['ilustrador'])
    nova_il.ilustrador_ajuste = get_artista(dados.iloc[i]['ilustrador_ajuste'])
    nova_il.credito = get_artista(dados.iloc[i]['credito'])
    nova_il.classificacao = get_none(dados.iloc[i]['classificacao'])
    nova_il.observacao_arte = dados.iloc[i]['observacao_arte']
    nova_il.pagamento = dados.iloc[i]['pagamento']

    nova_il.save()
