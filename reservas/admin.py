# reservas/admin.py
from django.contrib import admin
from .models import Sala # Importa o Model Sala

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    # Campos que serão exibidos na listagem do Admin
    list_display = ('nome', 'capacidade', 'tipo', 'localizacao')
    
    # Adiciona um campo de busca para facilitar a localização
    search_fields = ('nome', 'localizacao')
    
    # Adiciona filtros laterais
    list_filter = ('tipo', 'capacidade')