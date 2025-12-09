from django.urls import path, reverse_lazy
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
    path('registrar/done/', views.UsuarioCreateDone.as_view(), name='registrar_done'),
    path('gerenciar-usuarios/<int:pk>/', views.UsuarioUpdateView.as_view(), name='gerenciar_usuario'),
    path('gerenciar-usuarios/todos/', views.UsuarioListarTodosView.as_view(), name='gerenciar_usuarios_todos'),

    path('preferencias/colunas/', views.PreferenciasColunasUpdateView.as_view(), name='editar_preferencias_colunas'),



    # 1. Solicita o E-mail (envia o link)
    path('resetar-senha/', auth_views.PasswordResetView.as_view(
        template_name='usuario/recuperacao_senha/password_reset_form.html',
        email_template_name='usuario/recuperacao_senha/password_reset_email.html',
        subject_template_name='usuario/recuperacao_senha/password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),
    
    # 2. Informa que o e-mail foi enviado
    path('resetar-senha/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='usuario/recuperacao_senha/password_reset_done.html'
    ), name='password_reset_done'),
    
    # 3. Link de redefinição (Valida o token e mostra o formulário de nova senha)
    path('resetar-senha/confirmar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='usuario/recuperacao_senha/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),

    # 4. Confirmação de que a senha foi alterada
    path('resetar-senha/completo/', auth_views.PasswordResetCompleteView.as_view(
        template_name='usuario/recuperacao_senha/password_reset_complete.html'
    ), name='password_reset_complete'),
]