"""
URL configuration for ilustracoes project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from planilha import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ilustras/', views.ilustras, name='ilustras'),
    path('ilustras/regex/', views.ajuda_regex, name='ajuda_regex'),
    path('nova-ilustracao/', views.nova_ilustracao, name='nova_ilustracao'),
    path('ilustras-excluidas/', views.ilustras_excluidas, name='ilustras_excluidas'),
    path('ilustracao/<int:pk>/', views.IlustracaoUpdateView.as_view(), name='detalhe_ilustracao'),
    path('ilustracao/<int:pk>/deletar/', views.deletar_ilustracao, name='deletar_ilustracao'),
    path('ilustracao/<int:pk>/reativar/', views.reativar_ilustracao, name='reativar_ilustracao'),
    path('ilustras/upload/', views.UploadIlustracoesExcelView.as_view(), name='upload_ilustracoes_excel'),
    path('ilustras/import/', views.ImportarIlustracoesView.as_view(), name='import_ilustracoes_excel'),
    path('ilustras/download-excel/', views.DownloadTemplateDeImportarIlustracaoView.as_view(), name='download_template'),

    path('componentes/', views.componentes, name='componentes'),
    path('novo-componente/', views.novo_componente, name='novo_componente'),


    path('projetos/', views.projetos, name='projetos'),
    path('novo-projeto/', views.novo_projeto, name='novo_projeto'),

    path('ilustradores/', views.ilustradores, name='ilustradores'),
    path('novo-ilustrador/', views.novo_ilustrador, name='novo_ilustrador'),
    path('ilustradores-arquivados/', views.ilustradores_arquivados, name='ilustradores_arquivados'),
    path('ilustradores/<int:pk>/', views.IlustradorUpdateView.as_view(), name='detalhe_ilustrador'),
    path('ilustradores/<int:pk>/deletar/', views.deletar_ilustrador, name='deletar_ilustrador'),
    path('ilustradores/<int:pk>/reativar/', views.reativar_ilustrador, name='reativar_ilustrador'),

    path('creditos/', views.creditos, name='creditos'),
    path('creditos-arquivados/', views.creditos_arquivados, name='creditos_arquivados'),
    path('novo-credito/', views.novo_credito, name='novo_credito'),
    path('creditos/<int:pk>/', views.CreditoUpdateView.as_view(), name='detalhe_credito'),
    path('creditos/<int:pk>/deletar/', views.deletar_credito, name='deletar_credito'),
    path('creditos/<int:pk>/reativar/', views.reativar_credito, name='reativar_credito'),

    path('exportar/creditos/csv/', views.ExportarCreditosCSV.as_view(), name='exportar_creditos_csv'),
    path('exportar/excel/', views.ExportarIlustrasExcel.as_view(), name='exportar_ilustras_excel_completo'),
]
