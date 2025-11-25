"""
URL configuration for ifteca_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path, re_path
from django.http import HttpResponse

from auth_app import views as auth_views

urlpatterns = [
    # Responde ao pedido do Chrome DevTools para evitar 404s nos logs
    re_path(r'^\.well-known/appspecific/com\.chrome\.devtools\.json$', lambda request: HttpResponse(status=204)),
    # Django admin movido para evitar conflito com rota /admin/salas
    path("django-admin/", admin.site.urls),
    path("", include("salas.urls")),
    path("reservas/", include("reservas.urls")),
    path("login/", auth_views.login_page, name="login_page"),
    path("api/auth/", include("auth_app.urls")),
]
