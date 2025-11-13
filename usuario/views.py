from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin
from django.contrib.auth.models import User, Group


from .models import PreferenciasPreFiltro, PreenchimentoAutomaticoDeCampos
from .forms import PreferenciasPreFiltroModelForm, PreenchimentoAutomaticoDeCamposModelForm, UsuarioModelForm, UsuarioActivateDeactivateForm



class UsuarioUpdateView(GroupRequiredMixin, UpdateView):
    group_required = [u"Coordenador"]
    model = User
    form_class = UsuarioActivateDeactivateForm
    template_name = 'usuario/usuario_gerenciamento.html' 
    success_url = reverse_lazy('gerenciar_usuarios_todos')

class UsuarioListarTodosView(GroupRequiredMixin, TemplateView):
    group_required = [u"Coordenador"]
    template_name = 'usuario/usuario_gerenciamento_todos.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuarios_ativos'] = User.objects.filter(is_active=True)
        context['usuarios_desativados'] = User.objects.filter(is_active=False)
        return context

# 1. VIEW ROUTER (A View principal que decide para onde redirecionar)
class PreferenciasView(LoginRequiredMixin, View):
    """
    Verifica se o usuário já tem uma preferência salva.
    - Se tiver, redireciona para a View de Atualização (PreferenciasAtualizar).
    - Se não tiver, redireciona para a View de Criação (PreferenciasSalvar).
    """
    def get(self, request, *args, **kwargs):
        # Tenta buscar a preferência vinculada ao usuário logado
        try:
            preferencia = PreferenciasPreFiltro.objects.get(usuario=request.user)
            # Se a preferência existe, redireciona para a atualização
            return redirect('preferencias_atualizar', pk=preferencia.pk)
        except PreferenciasPreFiltro.DoesNotExist:
            # Se a preferência não existe, redireciona para o salvamento (criação)
            return redirect('preferencias_salvar')

# 2. VIEW DE CRIAÇÃO (Para o primeiro acesso)
class PreferenciasSalvar(LoginRequiredMixin, CreateView):
    """
    Permite ao usuário criar sua primeira preferência.
    """
    model = PreferenciasPreFiltro
    form_class = PreferenciasPreFiltroModelForm # Usando o Form para melhor controle
    template_name = 'usuario/preferencias.html'
    
    # Após salvar, redireciona de volta para o roteador (PreferenciasView)
    # que, agora, irá redirecionar para a Atualização
    success_url = reverse_lazy('preferencias') 
    
    def form_valid(self, form):
        # Vincula a preferência ao usuário logado antes de salvar
        form.instance.usuario = self.request.user
        return super().form_valid(form)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Define a variável de contexto 'is_coordenador'
        if self.request.user.is_authenticated:
            context['is_coordenador'] = self.request.user.groups.filter(name='Coordenador').exists()
        else:
            context['is_coordenador'] = False
        return context

# 3. VIEW DE ATUALIZAÇÃO (Para todos os acessos seguintes)
class PreferenciasAtualizar(LoginRequiredMixin, UpdateView):
    """
    Permite ao usuário atualizar sua preferência existente.
    """
    model = PreferenciasPreFiltro
    form_class = PreferenciasPreFiltroModelForm # Usando o Form
    template_name = 'usuario/preferencias.html'
    
    # Após atualizar, redireciona de volta para o roteador (PreferenciasView)
    success_url = reverse_lazy('preferencias') 
    
    def get_object(self, queryset=None):
        """
        Garante que o usuário só possa atualizar a sua própria preferência.
        Busca a preferência pelo PK fornecido na URL e vinculada ao usuário logado.
        """
        # Obter o PK da URL (que foi passado pelo PreferenciasView Router)
        pk = self.kwargs.get('pk')
        
        # Usa get_object_or_404 para buscar a preferência que corresponde ao PK 
        # E que pertença ao usuário logado (camada extra de segurança)
        return get_object_or_404(
            PreferenciasPreFiltro, 
            pk=pk, 
            usuario=self.request.user
        )
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Define a variável de contexto 'is_coordenador'
        if self.request.user.is_authenticated:
            context['is_coordenador'] = self.request.user.groups.filter(name='Coordenador').exists()
        else:
            context['is_coordenador'] = False
        return context



# 1. VIEW ROUTER (A View principal que decide para onde redirecionar)
class PreenchimentoAutomaticoDeCamposView(LoginRequiredMixin, View):
    """
    Verifica se o usuário já tem uma preferência salva.
    - Se tiver, redireciona para a View de Atualização (PreenchimentoAutomaticoDeCamposAtualizar).
    - Se não tiver, redireciona para a View de Criação (PreenchimentoAutomaticoDeCamposSalvar).
    """
    def get(self, request, *args, **kwargs):
        # Tenta buscar a preferência vinculada ao usuário logado
        try:
            preferencia = PreenchimentoAutomaticoDeCampos.objects.get(usuario=request.user)
            # Se a preferência existe, redireciona para a atualização
            return redirect('preenchimento_automatico_atualizar', pk=preferencia.pk)
        except PreenchimentoAutomaticoDeCampos.DoesNotExist:
            # Se a preferência não existe, redireciona para o salvamento (criação)
            return redirect('preenchimento_automatico_salvar')

# 2. VIEW DE CRIAÇÃO (Para o primeiro acesso)
class PreenchimentoAutomaticoDeCamposSalvar(LoginRequiredMixin, CreateView):
    """
    Permite ao usuário criar sua primeira preferência.
    """
    model = PreenchimentoAutomaticoDeCampos
    form_class = PreenchimentoAutomaticoDeCamposModelForm # Usando o Form para melhor controle
    template_name = 'usuario/preencimento_automatico.html'
    
    # Após salvar, redireciona de volta para o roteador (PreenchimentoAutomaticoDeCamposView)
    # que, agora, irá redirecionar para a Atualização
    success_url = reverse_lazy('preenchimento_automatico') 
    
    def form_valid(self, form):
        # Vincula a preferência ao usuário logado antes de salvar
        form.instance.usuario = self.request.user
        return super().form_valid(form)

# 3. VIEW DE ATUALIZAÇÃO (Para todos os acessos seguintes)
class PreenchimentoAutomaticoDeCamposAtualizar(LoginRequiredMixin, UpdateView):
    """
    Permite ao usuário atualizar sua preferência existente.
    """
    model = PreenchimentoAutomaticoDeCampos
    form_class = PreenchimentoAutomaticoDeCamposModelForm # Usando o Form
    template_name = 'usuario/preencimento_automatico.html'
    
    # Após atualizar, redireciona de volta para o roteador (PreenchimentoAutomaticoDeCamposView)
    success_url = reverse_lazy('preenchimento_automatico') 
    
    def get_object(self, queryset=None):
        """
        Garante que o usuário só possa atualizar a sua própria preferência.
        Busca a preferência pelo PK fornecido na URL e vinculada ao usuário logado.
        """
        # Obter o PK da URL (que foi passado pelo PreenchimentoAutomaticoDeCamposView Router)
        pk = self.kwargs.get('pk')
        
        # Usa get_object_or_404 para buscar a preferência que corresponde ao PK 
        # E que pertença ao usuário logado (camada extra de segurança)
        return get_object_or_404(
            PreenchimentoAutomaticoDeCampos, 
            pk=pk, 
            usuario=self.request.user
        )

class UsuarioCreate(CreateView):
    template_name = 'usuario/usuario_registro.html'
    form_class = UsuarioModelForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        grupo = get_object_or_404(Group, name='Comum')
        url = super().form_valid(form)
        self.object.groups.add(grupo)
        self.object.is_active = False
        self.object.save()
        return url
