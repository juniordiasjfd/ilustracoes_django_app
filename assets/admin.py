from django.contrib import admin
from .models import Dashboard


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo", "ordem")
    list_editable = ("ativo", "ordem")
    search_fields = ("nome",)
    list_filter = ("ativo",)
    ordering = ("ordem", "nome")