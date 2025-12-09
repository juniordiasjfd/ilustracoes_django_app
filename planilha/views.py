from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.edit import UpdateView
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin
from django.db.models import Q
import pandas
import datetime
from django.utils import timezone
from django.db import transaction
from django.http import HttpResponse
import csv


from .models import Projeto, Componente, Ilustracao, Ilustrador, Credito
from .forms import IlustracaoModelForm, ComponenteModelForm, ProjetoModelForm, IlustradorModelForm, CreditoModelForm, UploadExcelForm, UploadForCreateIlustracoesForm
from .filter import IlustracaoFilter
from usuario.models import PreferenciasPreFiltro, PreferenciasColunasTabela
from django.views.generic.edit import FormView
from .excel import create_excel
from io import BytesIO


def to_data_aware(date_naive):
    # 1. Crie o datetime naive
    # data_naive = datetime.datetime(2025, 11, 18, 0, 0, 0)
    # 2. Torne-o aware, usando o fuso horário configurado em settings.py (TIME_ZONE)
    return timezone.make_aware(date_naive)

def is_coordenador(user):
    return user.groups.filter(name='Coordenador').exists()


def index(request):
    return render(request, 'index.html')


def aplicar_pre_filtro_ilustras(request, queryset_base):
    """
    Aplica o pré-filtro de usuário (preferências) ao QuerySet base.
    Retorna o QuerySet filtrado e o status de 'pre_filtro_ativo'.
    """
    pre_filtro_ativo = False
    queryset_filtrado = queryset_base

    try:
        preferencias = PreferenciasPreFiltro.objects.get(usuario=request.user)
        filtro_q = Q()
        
        # Lógica de Pré-Filtro (idêntica à sua)
        
        #### Filtro por PROJETOS (ManyToMany)
        projetos_ids = preferencias.projetos.values_list('id', flat=True)
        if projetos_ids:
            filtro_q &= Q(projeto__id__in=projetos_ids)
            
        #### Filtro por COMPONENTES (ManyToMany)
        componentes_ids = preferencias.componentes.values_list('id', flat=True)
        if componentes_ids:
            filtro_q &= Q(componente__id__in=componentes_ids)
            
        #### Filtro por VOLUME (PositiveIntegerField)
        if preferencias.volume is not None:
            filtro_q &= Q(volume=preferencias.volume)
            
        if preferencias.projetos.exists() or preferencias.componentes.exists() or preferencias.volume is not None:
            pre_filtro_ativo = True
            
        queryset_filtrado = queryset_base.filter(filtro_q)
        
    except PreferenciasPreFiltro.DoesNotExist:
        # Se não houver preferências, retorna o QuerySet base
        pass
        
    return queryset_filtrado, pre_filtro_ativo

@login_required
def ilustras(request):
    ###############################################
    # adicionando filtro com as preferências do usuário
    # 1. Queryset Base: Apenas ilustrações ativas
    queryset_base = Ilustracao.objects.filter(
        ativo=True,
        projeto__ativo=True,
        componente__ativo=True,
        )
    num_linhas_total = queryset_base.count()

    queryset_filtrado, pre_filtro_ativo = aplicar_pre_filtro_ilustras(request, queryset_base)

    # # 2. Lógica do Pré-Filtro
    # pre_filtro_ativo = False
    # try:
    #     # Tenta buscar as preferências do usuário logado
    #     preferencias = PreferenciasPreFiltro.objects.get(usuario=request.user)
    #     # Inicia um filtro vazio
    #     filtro_q = Q()
    #     # Aplica filtros se os campos estiverem preenchidos nas preferências
    #     #### Filtro por PROJETOS (ManyToMany)
    #     projetos_ids = preferencias.projetos.values_list('id', flat=True)
    #     if projetos_ids:
    #         filtro_q &= Q(projeto__id__in=projetos_ids)
    #     #### Filtro por COMPONENTES (ManyToMany)
    #     componentes_ids = preferencias.componentes.values_list('id', flat=True)
    #     if componentes_ids:
    #         filtro_q &= Q(componente__id__in=componentes_ids)
    #     #### Filtro por VOLUME (PositiveIntegerField)
    #     if preferencias.volume is not None:
    #         # Note: O campo `volume` no modelo Ilustracao é IntegerField. 
    #         # Assumindo que você quer uma correspondência exata.
    #         filtro_q &= Q(volume=preferencias.volume)
    #     if preferencias.projetos.exists() or preferencias.componentes.exists() or preferencias.volume is not None:
    #         pre_filtro_ativo = True
    #     # Aplica o filtro Q ao queryset base
    #     # Se filtro_q estiver vazio (nenhuma preferência salva), aplica um filtro nulo (Q())
    #     # que não altera o queryset.
    #     queryset_filtrado = queryset_base.filter(filtro_q)
    # except PreferenciasPreFiltro.DoesNotExist:
    #     # Se o usuário não tem preferências salvas, usa o queryset base completo
    #     queryset_filtrado = queryset_base
    ###############################################
    try:
        preferencias_colunas = PreferenciasColunasTabela.objects.get(usuario=request.user)
    except PreferenciasColunasTabela.DoesNotExist:
        # Se não houver preferências salvas, cria-se um objeto temporário com os defaults
        preferencias_colunas = PreferenciasColunasTabela()
    ###############################################
    # filter = IlustracaoFilter(request.GET, queryset=Ilustracao.objects.filter(ativo=True))
    queryset_ordenado = queryset_filtrado.order_by('-lote')
    filter = IlustracaoFilter(request.GET, queryset=queryset_ordenado)
    num_linhas = filter.qs.count()
    context = {
        'ativo': True,
        'filter': filter,
        'num_linhas': num_linhas,
        'num_linhas_total': num_linhas_total,
        'pre_filtro_ativo': pre_filtro_ativo,
        'preferencias_colunas': preferencias_colunas,
    }
    return render(request, 'ilustras.html', context)
@login_required
def ilustras_excluidas(request):
    ###############################################
    # adicionando filtro com as preferências do usuário
    # 1. Queryset Base: Apenas ilustrações ativas
    queryset_base = Ilustracao.objects.filter(ativo=False)
    # 2. Lógica do Pré-Filtro
    pre_filtro_ativo = False
    try:
        # Tenta buscar as preferências do usuário logado
        preferencias = PreferenciasPreFiltro.objects.get(usuario=request.user)
        # Inicia um filtro vazio
        filtro_q = Q()
        # Aplica filtros se os campos estiverem preenchidos nas preferências
        #### Filtro por PROJETOS (ManyToMany)
        projetos_ids = preferencias.projetos.values_list('id', flat=True)
        if projetos_ids:
            filtro_q &= Q(projeto__id__in=projetos_ids)
        #### Filtro por COMPONENTES (ManyToMany)
        componentes_ids = preferencias.componentes.values_list('id', flat=True)
        if componentes_ids:
            filtro_q &= Q(componente__id__in=componentes_ids)
        #### Filtro por VOLUME (PositiveIntegerField)
        if preferencias.volume is not None:
            # Assumindo que você quer uma correspondência exata.
            filtro_q &= Q(volume=preferencias.volume)
        if preferencias.projetos.exists() or preferencias.componentes.exists() or preferencias.volume is not None:
            pre_filtro_ativo = True
        # Aplica o filtro Q ao queryset base
        # Se filtro_q estiver vazio (nenhuma preferência salva), aplica um filtro nulo (Q())
        # que não altera o queryset.
        queryset_filtrado = queryset_base.filter(filtro_q)
    except PreferenciasPreFiltro.DoesNotExist:
        # Se o usuário não tem preferências salvas, usa o queryset base completo
        queryset_filtrado = queryset_base
    ###############################################
    # filter = IlustracaoFilter(request.GET, queryset=Ilustracao.objects.filter(ativo=False))
    filter = IlustracaoFilter(request.GET, queryset=queryset_filtrado)
    num_linhas = filter.qs.count()
    context = {
        'ativo': False,
        'filter': filter,
        'num_linhas': num_linhas,
        'pre_filtro_ativo': pre_filtro_ativo,
    }
    return render(request, 'ilustras.html', context)
@login_required
def nova_ilustracao(request):
    if str(request.user) != 'AnonymousUser':
        if str(request.method) == 'POST':
            form = IlustracaoModelForm(request.POST, request=request)
            if form.is_valid():
                form.save()
                messages.success(request, 'Ilustração cadastrada.')
                form = IlustracaoModelForm(request=request)
            else:
                messages.error(request, 'Erro ao cadastrar.')
        else:
            form = IlustracaoModelForm(request=request)
        context = {
            'form': form,
            }
        return render(request, 'nova_ilustracao.html', context)
    else:
        return redirect('index')
class IlustracaoUpdateView(LoginRequiredMixin, UpdateView):
    # Modelo que será editado
    model = Ilustracao
    # REFERENCIANDO O SEU FORMULÁRIO
    form_class = IlustracaoModelForm
    # Template que será renderizado
    template_name = 'detalhe_ilustracao.html'
    # URL para onde o usuário será redirecionado após salvar
    success_url = reverse_lazy('ilustras')
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
@login_required
def deletar_ilustracao(request, pk):
    # Garante que a operação seja POST para segurança (requer o formulário)
    if request.method == 'POST':
        # 1. Busca o objeto
        ilustracao = get_object_or_404(Ilustracao, pk=pk)
        # 2. Altera o status 'ativo' para False
        ilustracao.ativo = False
        ilustracao.status = 'EXCLUÍDA'
        ilustracao.save()
        # 3. Redireciona para a lista (ou outra página)
        # Assumindo que você só mostra ilustrações ativas na lista 'ilustras'
        return redirect('ilustras')
        # Se alguém tentar acessar via GET, pode redirecionar ou retornar um erro
    return redirect('ilustras')
@login_required
def reativar_ilustracao(request, pk):
    # Garante que a operação seja POST para segurança (requer o formulário)
    if request.method == 'POST':
        # 1. Busca o objeto
        ilustracao = get_object_or_404(Ilustracao, pk=pk)
        # 2. Altera o status 'ativo' para False
        ilustracao.ativo = True
        ilustracao.save()
        # 3. Redireciona para a lista (ou outra página)
        # Assumindo que você só mostra ilustrações ativas na lista 'ilustras'
        return redirect('ilustras_excluidas')
        # Se alguém tentar acessar via GET, pode redirecionar ou retornar um erro
    return redirect('ilustras_excluidas')


@login_required
def componentes(request):
    componentes_ativos = Componente.objects.filter(ativo=True)
    componentes_arquivados = Componente.objects.filter(ativo=False)
    context = {
        'componentes_ativos': componentes_ativos,
        'componentes_arquivados': componentes_arquivados,
    }
    return render(request, 'componentes.html', context)
@login_required
@user_passes_test(is_coordenador)
def novo_componente(request):
    if str(request.user) != 'AnonymousUser':
        if request.method == 'POST':
            form = ComponenteModelForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Componente cadastrado.')
                form = ComponenteModelForm()
            else:
                messages.error(request, 'Erro ao cadastrar.')
        else:
            form = ComponenteModelForm()
        context = {
                'form': form,
            }
        return render(request, 'novo_componente.html', context)
    else:
        return redirect('index')


@login_required
def projetos(request):
    projetos_ativos = Projeto.objects.filter(ativo=True)
    projetos_arquivados = Projeto.objects.filter(ativo=False)
    context = {
        'projetos_ativos': projetos_ativos,
        'projetos_arquivados': projetos_arquivados,
    }
    return render(request, 'projetos.html', context)
@login_required
@user_passes_test(is_coordenador)
def novo_projeto(request):
    if str(request.user) != 'AnonymousUser':
        if request.method == 'POST':
            form = ProjetoModelForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Projeto cadastrado.')
                form = ProjetoModelForm()
            else:
                messages.error(request, 'Erro ao cadastrar.')
        else:
            form = ProjetoModelForm()
        context = {
            'form': form,
        }
        return render(request, 'novo_projeto.html', context)
    else:
        return redirect('index')


@login_required
def ilustradores(request):
    artistas = Ilustrador.objects.filter(ativo=True)
    context = {
        'artistas': artistas,
        'ativo': True,
        'num_linhas': artistas.count(),
    }
    return render(request, 'ilustradores.html', context)
@login_required
def ilustradores_arquivados(request):
    artistas = Ilustrador.objects.filter(ativo=False)
    context = {
        'artistas': artistas,
        'ativo': False,
        'num_linhas': artistas.count(),
    }
    return render(request, 'ilustradores.html', context)
@login_required
@user_passes_test(is_coordenador)
def novo_ilustrador(request):
    if str(request.user) != 'AnonymousUser':
        if request.method == 'POST':
            form = IlustradorModelForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Ilustrador cadastrado.')
                form = IlustradorModelForm()
            else:
                messages.error(request, 'Erro ao cadastrar.')
        else:
            form = IlustradorModelForm()
        context = {
            'form': form,
        }
        return render(request, 'novo_ilustrador.html', context)
    else:
        return redirect('index')
class IlustradorUpdateView(GroupRequiredMixin, LoginRequiredMixin, UpdateView):
    group_required = [u"Coordenador"]
    # Modelo que será editado
    model = Ilustrador
    # REFERENCIANDO O SEU FORMULÁRIO
    form_class = IlustradorModelForm
    # Template que será renderizado
    template_name = 'detalhe_ilustrador.html'
    # URL para onde o usuário será redirecionado após salvar
    success_url = reverse_lazy('ilustradores')
@login_required
def deletar_ilustrador(request, pk):
    # Garante que a operação seja POST para segurança (requer o formulário)
    if request.method == 'POST':
        # 1. Busca o objeto
        ilustrador = get_object_or_404(Ilustrador, pk=pk)
        # 2. Altera o status 'ativo' para False
        ilustrador.ativo = False
        ilustrador.save()
        # 3. Redireciona para a lista (ou outra página)
        # Assumindo que você só mostra ilustrações ativas na lista 'ilustras'
        return redirect('ilustradores')
        # Se alguém tentar acessar via GET, pode redirecionar ou retornar um erro
    return redirect('ilustradores')
@login_required
def reativar_ilustrador(request, pk):
    # Garante que a operação seja POST para segurança (requer o formulário)
    if request.method == 'POST':
        # 1. Busca o objeto
        ilustrador = get_object_or_404(Ilustrador, pk=pk)
        # 2. Altera o status 'ativo' para False
        ilustrador.ativo = True
        ilustrador.save()
        # 3. Redireciona para a lista (ou outra página)
        # Assumindo que você só mostra ilustrações ativas na lista 'ilustras'
        return redirect('ilustradores')
        # Se alguém tentar acessar via GET, pode redirecionar ou retornar um erro
    return redirect('ilustradores')


@login_required
def creditos(request):
    artistas = Credito.objects.filter(ativo=True)
    context = {
        'artistas': artistas,
        'ativo': True,
        'num_linhas': artistas.count(),
    }
    return render(request, 'creditos.html', context)
@login_required
@user_passes_test(is_coordenador)
def novo_credito(request):
    if str(request.user) != 'AnonymousUser':
        if request.method == 'POST':
            form = CreditoModelForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Crédito cadastrado.')
                form = CreditoModelForm()
            else:
                messages.error(request, 'Erro ao cadastrar.')
        else:
            form = CreditoModelForm()
        context = {
            'form': form,
        }
        return render(request, 'novo_credito.html', context)
    else:
        return redirect('index')
class CreditoUpdateView(GroupRequiredMixin, LoginRequiredMixin, UpdateView):
    group_required = [u"Coordenador"]
    # Modelo que será editado
    model = Credito
    # REFERENCIANDO O SEU FORMULÁRIO
    form_class = CreditoModelForm
    # Template que será renderizado
    template_name = 'detalhe_credito.html'
    # URL para onde o usuário será redirecionado após salvar
    success_url = reverse_lazy('creditos')
@login_required
def deletar_credito(request, pk):
    # Garante que a operação seja POST para segurança (requer o formulário)
    if request.method == 'POST':
        # 1. Busca o objeto
        credito = get_object_or_404(Credito, pk=pk)
        # 2. Altera o status 'ativo' para False
        credito.ativo = False
        credito.save()
        # 3. Redireciona para a lista (ou outra página)
        # Assumindo que você só mostra ilustrações ativas na lista 'ilustras'
        return redirect('creditos')
        # Se alguém tentar acessar via GET, pode redirecionar ou retornar um erro
    return redirect('creditos')
@login_required
def reativar_credito(request, pk):
    # Garante que a operação seja POST para segurança (requer o formulário)
    if request.method == 'POST':
        # 1. Busca o objeto
        credito = get_object_or_404(Credito, pk=pk)
        # 2. Altera o status 'ativo' para False
        credito.ativo = True
        credito.save()
        # 3. Redireciona para a lista (ou outra página)
        # Assumindo que você só mostra ilustrações ativas na lista 'ilustras'
        return redirect('creditos')
        # Se alguém tentar acessar via GET, pode redirecionar ou retornar um erro
    return redirect('creditos')
@login_required
def creditos_arquivados(request):
    artistas = Credito.objects.filter(ativo=False)
    context = {
        'artistas': artistas,
        'ativo': False,
        'num_linhas': artistas.count(),
    }
    return render(request, 'creditos.html', context)


def ajuda_regex(request):
    return render(request, 'ajuda_regex.html')


class UploadIlustracoesExcelView(LoginRequiredMixin, FormView):
    template_name = 'upload_ilustracoes.html'
    form_class = UploadExcelForm
    success_url = reverse_lazy('ilustras')

    def form_valid(self, form):
        """
        Este método é chamado quando o formulário é submetido e validado.
        Aqui processamos o arquivo Excel e atualizamos o banco de dados.
        """
        request = self.request
        excel_file = request.FILES['arquivo_excel']
        try:
            # 1. Leitura do arquivo
            # Lê a primeira aba, assumindo que o cabeçalho está na primeira linha (index 0)
            # excel_file = r'C:\Users\junior.dias\Downloads\ilustracoes (1).xlsx'
            df = pandas.read_excel(excel_file, header=0)
            
            # 2. Mapeamento de Colunas e Preparações
            df.rename(columns={
                'Retranca': 'retranca', 
                'Status': 'status', 
                'Pagamento': 'pagamento',
                'Lote': 'lote',
                'Data de liberação para arte': 'data_liberacao_para_arte',
                'Data de envio do pedido': 'data_envio_pedido',
                'Data de recebimento do rafe': 'data_recebimento_rafe',
                'Data de retorno do rafe': 'data_retorno_rafe',
                'Data de recebimento da finalizada': 'data_recebimento_finalizada',
            }, inplace=True)
            
            # Obtém as retrancas do Excel para buscar os objetos no DB
            # retrancas_do_excel = df['retranca'].dropna().astype(str).str.strip().tolist()
            pks_do_excel = df['pk'].dropna().tolist()
            # Busca todos os objetos em uma única consulta (in_bulk cria um dict {pk: objeto})
            ilustracoes_db = Ilustracao.objects.filter(pk__in=pks_do_excel).in_bulk(field_name='pk')
            
            ilustracoes_para_atualizar = []
            lista_de_campos_a_atualizar = []
            
            # 3. Itera e Prepara a Atualização
            '''
            for index, row in df.iterrows():
                break
            '''
            for index, row in df.iterrows():
                pk = row.get('pk', '')
                
                if pk and pk in ilustracoes_db:
                    il: Ilustracao = ilustracoes_db[pk]
                    
                    # --- Processa e valida o novo STATUS ---
                    novo_status_label = str(row.get('status', '')).strip()
                    # Garante que o valor do Excel seja um valor válido do StatusChoices
                    # O .values contém os valores internos (e.g., 'EDICAO_EQUIPE')
                    if novo_status_label in Ilustracao.StatusChoices.values:
                        if il.status != novo_status_label:
                            il.status = novo_status_label
                            lista_de_campos_a_atualizar.append('status')
                            if il not in ilustracoes_para_atualizar: 
                                ilustracoes_para_atualizar.append(il)

                    # --- Processa e valida o novo PAGAMENTO ---
                    novo_pagamento_label = str(row.get('pagamento', '')).strip()
                    # Garante que o valor do Excel seja um valor válido do PagamentoChoices
                    if novo_pagamento_label in Ilustracao.PagamentoChoices.values:
                        if il.pagamento != novo_pagamento_label:
                            il.pagamento = novo_pagamento_label
                            lista_de_campos_a_atualizar.append('pagamento')
                            if il not in ilustracoes_para_atualizar: 
                                ilustracoes_para_atualizar.append(il)
                    
                    # -- Processa e valida o LOTE ---
                    processar = False
                    novo_lote_label = str(row.get('lote','')).strip()
                    # print('novo_lote_label',novo_lote_label, il)
                    if novo_lote_label == 'nan':
                        novo_lote_label = None
                    try:
                        novo_lote_label = (None if novo_lote_label == None else int(float(novo_lote_label)))
                        if novo_lote_label == None:
                            processar = True
                        elif novo_lote_label >= 0:
                            processar = True
                        if processar:
                            if il.lote != novo_lote_label:
                                il.lote = novo_lote_label
                                lista_de_campos_a_atualizar.append('lote')
                                if il not in ilustracoes_para_atualizar:
                                    ilustracoes_para_atualizar.append(il)
                    except: pass

                    # --- Processa e valida a data -- 
                    processar = False
                    nova_data_liberacao_para_arte_label = row.get('data_liberacao_para_arte','')
                    if type(nova_data_liberacao_para_arte_label) == str and '/' in nova_data_liberacao_para_arte_label:
                        nova_data_liberacao_para_arte_label = datetime.datetime.strptime(nova_data_liberacao_para_arte_label, '%d/%m/%Y')
                        processar = True
                    elif type(nova_data_liberacao_para_arte_label) == pandas.Timestamp:
                        processar = True
                        nova_data_liberacao_para_arte_label = nova_data_liberacao_para_arte_label.to_pydatetime()
                    if processar:
                        if il.data_liberacao_para_arte != nova_data_liberacao_para_arte_label:
                            il.data_liberacao_para_arte = to_data_aware(nova_data_liberacao_para_arte_label)
                            lista_de_campos_a_atualizar.append('data_liberacao_para_arte')
                            if il not in ilustracoes_para_atualizar:
                                ilustracoes_para_atualizar.append(il)
                    
                    processar = False
                    nova_data_envio_pedido_label = row.get('data_envio_pedido','')
                    if type(nova_data_envio_pedido_label) == str and '/' in nova_data_envio_pedido_label:
                        nova_data_envio_pedido_label = datetime.datetime.strptime(nova_data_envio_pedido_label, '%d/%m/%Y')
                        processar = True
                    elif type(nova_data_envio_pedido_label) == pandas.Timestamp:
                        processar = True
                        nova_data_envio_pedido_label = nova_data_envio_pedido_label.to_pydatetime()
                    if processar:
                        if il.data_envio_pedido != nova_data_envio_pedido_label:
                            il.data_envio_pedido = to_data_aware(nova_data_envio_pedido_label)
                            lista_de_campos_a_atualizar.append('data_envio_pedido')
                            if il not in ilustracoes_para_atualizar:
                                ilustracoes_para_atualizar.append(il)
                    
                    processar = False
                    nova_data_recebimento_rafe_label = row.get('data_recebimento_rafe','')
                    if type(nova_data_recebimento_rafe_label) == str and '/' in nova_data_recebimento_rafe_label:
                        nova_data_recebimento_rafe_label = datetime.datetime.strptime(nova_data_recebimento_rafe_label, '%d/%m/%Y')
                        processar = True
                    elif type(nova_data_recebimento_rafe_label) == pandas.Timestamp:
                        processar = True
                        nova_data_recebimento_rafe_label = nova_data_recebimento_rafe_label.to_pydatetime()
                    if processar:
                        if il.data_recebimento_rafe != nova_data_recebimento_rafe_label:
                            il.data_recebimento_rafe = to_data_aware(nova_data_recebimento_rafe_label)
                            lista_de_campos_a_atualizar.append('data_recebimento_rafe')
                            if il not in ilustracoes_para_atualizar:
                                ilustracoes_para_atualizar.append(il)
                    
                    processar = False
                    nova_data_retorno_rafe_label = row.get('data_retorno_rafe','')
                    if type(nova_data_retorno_rafe_label) == str and '/' in nova_data_retorno_rafe_label:
                        nova_data_retorno_rafe_label = datetime.datetime.strptime(nova_data_retorno_rafe_label, '%d/%m/%Y')
                        processar = True
                    elif type(nova_data_retorno_rafe_label) == pandas.Timestamp:
                        processar = True
                        nova_data_retorno_rafe_label = nova_data_retorno_rafe_label.to_pydatetime()
                    if processar:
                        if il.data_retorno_rafe != nova_data_retorno_rafe_label:
                            il.data_retorno_rafe = to_data_aware(nova_data_retorno_rafe_label)
                            lista_de_campos_a_atualizar.append('data_retorno_rafe')
                            if il not in ilustracoes_para_atualizar:
                                ilustracoes_para_atualizar.append(il)
                    
                    processar = False
                    nova_data_recebimento_finalizada_label = row.get('data_recebimento_finalizada','')
                    # print(nova_data_recebimento_finalizada_label)
                    if type(nova_data_recebimento_finalizada_label) == str and '/' in nova_data_recebimento_finalizada_label:
                        nova_data_recebimento_finalizada_label = datetime.datetime.strptime(nova_data_recebimento_finalizada_label, '%d/%m/%Y')
                        processar = True
                    elif type(nova_data_recebimento_finalizada_label) == pandas.Timestamp:
                        processar = True
                        nova_data_recebimento_finalizada_label = nova_data_recebimento_finalizada_label.to_pydatetime()
                    if processar:
                        if il.data_recebimento_finalizada != nova_data_recebimento_finalizada_label:
                            il.data_recebimento_finalizada = to_data_aware(nova_data_recebimento_finalizada_label)
                            lista_de_campos_a_atualizar.append('data_recebimento_finalizada')
                            if il not in ilustracoes_para_atualizar:
                                ilustracoes_para_atualizar.append(il)

            # 4. Executa a Atualização em Massa
            if ilustracoes_para_atualizar:
                with transaction.atomic():
                    # Utiliza bulk_update para fazer a atualização em massa eficiente
                    Ilustracao.objects.bulk_update(
                        ilustracoes_para_atualizar, 
                        lista_de_campos_a_atualizar
                    )
                messages.success(request, f'{len(ilustracoes_para_atualizar)} ilustrações atualizadas com sucesso via Excel!')
            else:
                messages.info(request, 'Nenhuma alteração detectada nas ilustrações fornecidas.')

            # Chama o método pai (que lida com o redirecionamento para success_url)
            return super().form_valid(form)
            
        except Exception as e:
            # Trata erros de leitura de arquivo ou problemas na lógica
            messages.error(request, f'Erro ao processar o arquivo: {e}')
            print(f"Erro de processamento do Excel: {e}")
            # Se houver erro, retorna ao formulário com o contexto do erro
            return self.form_invalid(form)


class ImportarIlustracoesView(LoginRequiredMixin, FormView):
    template_name = "importar_ilustracoes.html"
    form_class = UploadForCreateIlustracoesForm
    success_url = reverse_lazy("import_ilustracoes_excel")

    # -------------------------------
    # MAPEAMENTO: verbose_name → field
    # -------------------------------
    MAP_COLUNAS = {
        "Retranca": "retranca",
        "Status": "status",
        "Categoria": "categoria",
        "Localização": "localizacao",
        "Volume": "volume",
        "Unidade": "unidade",
        "Capítulo ou seção": "capitulo_secao",
        "Página": "pagina",
        "Tipo": "tipo",
        "Descrição": "descricao",
        "Observação editorial e núcleo": "observacao_edit_nuc",
        "Lote": "lote",
        "Data de liberação do lote": "data_liberacao_para_arte",
        "Data de envio do pedido": "data_envio_pedido",
        "Data de recebimento do rafe": "data_recebimento_rafe",
        "Data de retorno do rafe": "data_retorno_rafe",
        "Data de recebimento da finalizada": "data_recebimento_finalizada",
        "Classificação": "classificacao",
        "Crédito": "credito",
        "Ilustrador resgate": "ilustrador_resgate",
        "Ilustrador criação": "ilustrador",
        "Ilustrador ajuste": "ilustrador_ajuste",
        "Observação da arte": "observacao_arte",
        "Pagamento": "pagamento",
        "Projeto": "projeto",
        "Componente": "componente",
    }

    # ------------------------------------
    # CAMPOS OBRIGATÓRIOS (do modelo)
    # ------------------------------------
    COLUNAS_OBRIGATORIAS = [
        "retranca",
        "descricao",
        "volume",
        "status",
        "categoria",
        "localizacao",
        "tipo",
        "projeto",
        "componente",
    ]
    def _limpar_sigla_ilustrador(self, valor):
        """
        Aceita 'SIGLA' ou 'SIGLA - NOME' e retorna apenas a SIGLA.
        Retorna None se o valor for nulo ou vazio após a limpeza.
        """
        if pandas.notna(valor) and valor:
            valor_str = str(valor).strip()
            
            # Se contiver o separador ' - ', pega o primeiro elemento
            if ' - ' in valor_str:
                return valor_str.split(' - ')[0].strip()
            
            # Caso contrário, assume que é apenas a sigla
            return valor_str
            
        return None
    def form_valid(self, form):
        arquivo = form.cleaned_data["arquivo"]

        try:
            df = pandas.read_excel(arquivo)
        except Exception as e:
            messages.error(self.request, f"Erro ao ler o arquivo: {e}")
            return self.form_invalid(form)

        # Renomeia colunas com base no verbose_name
        df = df.rename(columns={c: self.MAP_COLUNAS[c] for c in df.columns if c in self.MAP_COLUNAS})

        # Verifica colunas obrigatórias
        faltando = [col for col in self.COLUNAS_OBRIGATORIAS if col not in df.columns]

        if faltando:
            messages.error(
                self.request,
                f"Colunas obrigatórias ausentes no Excel: {', '.join(faltando)}"
            )
            return self.form_invalid(form)

        criados = 0
        erros = []

        for index, row in df.iterrows():
            try:
                # -----------------------------
                # 1. Foreign Keys Obrigatórias
                # -----------------------------
                try:
                    projeto = Projeto.objects.get(nome=row["projeto"])
                except Projeto.DoesNotExist:
                    raise Exception(f"Projeto '{row['projeto']}' não encontrado.")

                try:
                    componente = Componente.objects.get(nome=row["componente"])
                except Componente.DoesNotExist:
                    raise Exception(f"Componente '{row['componente']}' não encontrado.")
                
                # -----------------------------
                # 2. Mapeamento de Dados
                # -----------------------------
                
                # Campos de Data (requerem conversão para None se forem NaT/NaN)
                data_liberacao_para_arte = row.get("data_liberacao_para_arte")
                if pandas.notna(data_liberacao_para_arte):
                    # Se for uma data válida, garante que ela esteja em formato Python (date ou datetime)
                    if isinstance(data_liberacao_para_arte, pandas.Timestamp):
                        data_liberacao_para_arte = data_liberacao_para_arte.date()
                else:
                    data_liberacao_para_arte = None

                data_envio_pedido = row.get("data_envio_pedido")
                if pandas.notna(data_envio_pedido):
                    if isinstance(data_envio_pedido, pandas.Timestamp):
                        data_envio_pedido = data_envio_pedido.date()
                else:
                    data_envio_pedido = None
                    
                data_recebimento_rafe = row.get("data_recebimento_rafe")
                if pandas.notna(data_recebimento_rafe):
                    if isinstance(data_recebimento_rafe, pandas.Timestamp):
                        data_recebimento_rafe = data_recebimento_rafe.date()
                else:
                    data_recebimento_rafe = None
                    
                data_retorno_rafe = row.get("data_retorno_rafe")
                if pandas.notna(data_retorno_rafe):
                    if isinstance(data_retorno_rafe, pandas.Timestamp):
                        data_retorno_rafe = data_retorno_rafe.date()
                else:
                    data_retorno_rafe = None
                    
                data_recebimento_finalizada = row.get("data_recebimento_finalizada")
                if pandas.notna(data_recebimento_finalizada):
                    if isinstance(data_recebimento_finalizada, pandas.Timestamp):
                        data_recebimento_finalizada = data_recebimento_finalizada.date()
                else:
                    data_recebimento_finalizada = None

                # Campos Numéricos/String Opcionais (garantir None em caso de NaN)
                pagina = row.get("pagina") if pandas.notna(row.get("pagina")) else None
                unidade = row.get("unidade") if pandas.notna(row.get("unidade")) else None
                capitulo_secao = row.get("capitulo_secao") if pandas.notna(row.get("capitulo_secao")) else None
                observacao_edit_nuc = row.get("observacao_edit_nuc") if pandas.notna(row.get("observacao_edit_nuc")) else None
                
                # CORREÇÃO PARA O ERRO 'lote expected a number but got nan'
                lote = row.get("lote") if pandas.notna(row.get("lote")) else None
                
                classificacao = row.get("classificacao") if pandas.notna(row.get("classificacao")) else None
                observacao_arte = row.get("observacao_arte") if pandas.notna(row.get("observacao_arte")) else None
                pagamento = row.get("pagamento") if pandas.notna(row.get("pagamento")) else None


                # -----------------------------
                # 3. Criação da Ilustração
                # -----------------------------
                
                ilustracao = Ilustracao(
                    retranca=row["retranca"],
                    descricao=row["descricao"],
                    volume=row["volume"],

                    pagina=pagina,
                    unidade=unidade,
                    capitulo_secao=capitulo_secao,
                    observacao_edit_nuc=observacao_edit_nuc,
                    lote=lote, # Agora pode ser None
                    
                    # Campos de Data corrigidos
                    data_liberacao_para_arte=data_liberacao_para_arte,
                    data_envio_pedido=data_envio_pedido,
                    data_recebimento_rafe=data_recebimento_rafe,
                    data_retorno_rafe=data_retorno_rafe,
                    data_recebimento_finalizada=data_recebimento_finalizada,
                    
                    classificacao=classificacao,
                    observacao_arte=observacao_arte,

                    status=row["status"],
                    categoria=row["categoria"],
                    localizacao=row["localizacao"],
                    tipo=row["tipo"],
                    pagamento=pagamento,

                    projeto=projeto,
                    componente=componente,
                )

                # ---------------------------------------------
                # 4. FKs opcionais de Ilustrador (com flexibilidade de entrada)
                # ---------------------------------------------

                # 1. Ilustrador criação (campo 'ilustrador')
                valor_excel = row.get("ilustrador")
                sigla_ilustrador = self._limpar_sigla_ilustrador(valor_excel)
                if sigla_ilustrador:
                    try:
                        ilustracao.ilustrador = Ilustrador.objects.get(sigla=sigla_ilustrador)
                    except Ilustrador.DoesNotExist:
                        raise Exception(f"Ilustrador de criação com sigla '{sigla_ilustrador}' (valor original: '{valor_excel}') não encontrado.")

                # 2. Ilustrador resgate (campo 'ilustrador_resgate')
                valor_excel = row.get("ilustrador_resgate")
                sigla_resgate = self._limpar_sigla_ilustrador(valor_excel)
                if sigla_resgate:
                    try:
                        ilustracao.ilustrador_resgate = Ilustrador.objects.get(sigla=sigla_resgate)
                    except Ilustrador.DoesNotExist:
                        raise Exception(f"Ilustrador de resgate com sigla '{sigla_resgate}' (valor original: '{valor_excel}') não encontrado.")

                # 3. Ilustrador ajuste (campo 'ilustrador_ajuste')
                valor_excel = row.get("ilustrador_ajuste")
                sigla_ajuste = self._limpar_sigla_ilustrador(valor_excel)
                if sigla_ajuste:
                    try:
                        ilustracao.ilustrador_ajuste = Ilustrador.objects.get(sigla=sigla_ajuste)
                    except Ilustrador.DoesNotExist:
                        raise Exception(f"Ilustrador de ajuste com sigla '{sigla_ajuste}' (valor original: '{valor_excel}') não encontrado.")

                # 4. Crédito (mantido como está, buscando pelo nome)
                if pandas.notna(row.get("credito")):
                    nome_credito = row["credito"]
                    try:
                        ilustracao.credito = Credito.objects.get(nome=nome_credito)
                    except Credito.DoesNotExist:
                        raise Exception(f"Crédito '{nome_credito}' não encontrado.")

                ilustracao.save()
                criados += 1

            except Exception as e:
                erros.append(f"Linha {index+2}: {e}")

        if criados:
            messages.success(self.request, f"{criados} ilustrações importadas com sucesso!")

        if erros:
            messages.warning(
                self.request,
                "Algumas linhas não foram importadas:<br>" + "<br>".join(erros)
            )

        return super().form_valid(form)

class DownloadTemplateDeImportarIlustracaoView(View):
    """
    View baseada em Classe (CBV) para gerar e servir o arquivo Excel 
    com validação de dados para download.
    """
    def get(self, request, *args, **kwargs):
        # 1. Obter o Workbook (chamando sua função)
        workbook = create_excel()
        
        # 2. Configurar o buffer de memória (BytesIO)
        output = BytesIO()
        workbook.save(output)
        output.seek(0) # Retorna ao início do buffer
        
        # 3. Configurar a Resposta HTTP
        
        # Define o tipo MIME padrão para arquivos .xlsx
        response = HttpResponse(
            output.read(), 
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # 4. Configurar os cabeçalhos para download
        
        data_formatada = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"template_ilustracao_vazio_{data_formatada}.xlsx"
        
        # O cabeçalho 'Content-Disposition' informa ao navegador que é um anexo
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response

    

class ExportarCreditosCSV(View):
    """
    Exporta Retranca e Crédito das Ilustrações Filtradas em formato CSV.
    """
    
    def get(self, request, *args, **kwargs):

        

        # 1. Definir o QuerySet Base
        queryset_base = Ilustracao.objects.filter(
            ativo=True,
            projeto__ativo=True,
            componente__ativo=True
        ).order_by('-lote')

        queryset_filtrado_pelo_prefiro, _ = aplicar_pre_filtro_ilustras(request, queryset_base)
        queryset_ordenado = queryset_filtrado_pelo_prefiro.order_by('-lote')

        # 2. Aplicar os filtros da requisição (request.GET)
        # O self.request.GET contém os mesmos parâmetros da URL.
        filtro = IlustracaoFilter(self.request.GET, queryset=queryset_ordenado)
        ilustracoes_filtradas = filtro.qs
        
        # 3. Preparar a resposta CSV
        response = HttpResponse(
            content_type='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename="creditos_ilustracoes_filtradas.csv"'
            }
        )
        response.write(u'\ufeff'.encode('utf8'))

        writer = csv.writer(response)
        
        # Cabeçalho do CSV
        writer.writerow(['retranca', 'credito'])

        # 4. Escrever os dados no CSV
        for ilustracao in ilustracoes_filtradas:
            # Acessa o nome do crédito (assumindo que 'credito' é um ForeignKey com campo 'nome')
            # Use o operador ternário para lidar com campos nulos.
            credito_nome = ilustracao.credito.nome if ilustracao.credito else ""
            
            # Escreve a linha no CSV
            writer.writerow([
                ilustracao.retranca,
                credito_nome
            ])

        return response

