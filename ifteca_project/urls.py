"""
URL configuration for ifteca_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from salas import views as salas_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Alias direto para a listagem e formulÁrio (mock admin sem login nesta sprint)
    path("salas/listar/", salas_views.gerenciar_salas, name="listar_salas"),
    path("forms/", salas_views.criar_sala, name="form_criar_sala_root"),
    path("", include("salas.urls")),
    path("reservas/", include("reservas.urls")),
    path('api/auth/', include('auth_app.urls')),
]
