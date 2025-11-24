from django.contrib import admin

from .models import Sala


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ("nome", "capacidade", "tipo", "criado_em")
    search_fields = ("nome", "tipo")
    list_filter = ("tipo",)
