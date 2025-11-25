from django.contrib import admin
from .models import Reserva


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("sala", "usuario", "inicio", "fim")
    search_fields = ("usuario", "sala__nome")
    list_filter = ("sala", "inicio")