from django.contrib import admin
from .models import Projeto, Componente, Ilustrador, Credito


class ComponenteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'criado_em', 'modificado_em', 'criado_por', 'atualizado_por', 'ativo')

admin.site.register(Componente, ComponenteAdmin)

class ProjetoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'editora', 'ciclo', 'criado_em', 'modificado_em', 'criado_por', 'atualizado_por', 'ativo')

admin.site.register(Projeto, ProjetoAdmin)

class IlustradorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'criado_em', 'modificado_em', 'criado_por', 'atualizado_por', 'ativo')

admin.site.register(Ilustrador, IlustradorAdmin)

class CreditoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'criado_em', 'modificado_em', 'criado_por', 'atualizado_por', 'ativo')
    filter_horizontal = ('projetos','componentes')

admin.site.register(Credito, CreditoAdmin)
