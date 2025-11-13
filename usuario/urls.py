from django.urls import path
from django.contrib.auth import views as auth_views
from usuario import views


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(
            template_name='usuario/login.html'
        ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='login'
        ), name='logout'),
    path('preferencias/', views.PreferenciasView.as_view(), name='preferencias'),
    path('preferencias/salvar/', views.PreferenciasSalvar.as_view(), name='preferencias_salvar'),
    path('preferencias/atualizar/<int:pk>/', views.PreferenciasAtualizar.as_view(), name='preferencias_atualizar'),

    path('preferencias/preenchimento-default/', views.PreenchimentoAutomaticoDeCamposView.as_view(), name='preenchimento_automatico'),
    path('preferencias/preenchimento-default/salvar/', views.PreenchimentoAutomaticoDeCamposSalvar.as_view(), name='preenchimento_automatico_salvar'),
    path('preferencias/preenchimento-default/atualizar/<int:pk>/', views.PreenchimentoAutomaticoDeCamposAtualizar.as_view(), name='preenchimento_automatico_atualizar'),
    path('registrar/', views.UsuarioCreate.as_view(), name='registrar'),
    path('gerenciar-usuarios/<int:pk>/', views.UsuarioUpdateView.as_view(), name='gerenciar_usuario'),
    path('gerenciar-usuarios/todos/', views.UsuarioListarTodosView.as_view(), name='gerenciar_usuarios_todos'),
]