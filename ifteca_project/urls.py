"""
URL configuration for ifteca_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path, re_path
from django.http import HttpResponse
from django.shortcuts import redirect

from auth_app import views as auth_views
from reservas import views as reservas_views

urlpatterns = [
    # Responde ao pedido do Chrome DevTools para evitar 404s nos logs
    re_path(r'^\.well-known/appspecific/com\.chrome\.devtools\.json$', lambda request: HttpResponse(status=204)),
    # Redireciona raiz para login
    path("", lambda request: redirect("login_page")),
    # Django admin movido para evitar conflito com rota /admin/salas
    path("django-admin/", admin.site.urls),
    
    # APIs públicas (sem prefixo /reservas/)
    path("api/salas/<int:sala_id>/horarios/", reservas_views.api_horarios_disponiveis, name="api_horarios_disponiveis"),
    path("api/reservas/criar/", reservas_views.api_criar_reserva, name="api_criar_reserva"),
    # Atalho para interface administrativa de reservas (compatibilidade /admin/reserva)
    path("admin/reserva/", lambda request: redirect('/reservas/admin/reserva/')),
    
    path("", include("salas.urls")),
    path("reservas/", include("reservas.urls")),
    path("login/", auth_views.login_page, name="login_page"),
    path("logout/", auth_views.logout_view, name="logout"),
    path("api/auth/", include("auth_app.urls")),
]
