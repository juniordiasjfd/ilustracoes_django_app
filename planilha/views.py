from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin
from django.db.models import Q

from .models import Projeto, Componente, Ilustracao, Ilustrador, Credito
from .forms import IlustracaoModelForm, ComponenteModelForm, ProjetoModelForm, IlustradorModelForm, CreditoModelForm
from .filter import IlustracaoFilter
from usuario.models import PreferenciasPreFiltro


def is_coordenador(user):
    return user.groups.filter(name='Coordenador').exists()


def index(request):
    return render(request, 'index.html')


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
            # Note: O campo `volume` no modelo Ilustracao é IntegerField. 
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
    # filter = IlustracaoFilter(request.GET, queryset=Ilustracao.objects.filter(ativo=True))
    filter = IlustracaoFilter(request.GET, queryset=queryset_filtrado)
    num_linhas = filter.qs.count()
    context = {
        'ativo': True,
        'filter': filter,
        'num_linhas': num_linhas,
        'pre_filtro_ativo': pre_filtro_ativo,
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