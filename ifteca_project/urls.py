"""
URL configuration for ifteca_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path

from auth_app import views as auth_views

urlpatterns = [
    # Django admin movido para evitar conflito com rota /admin/salas
    path("django-admin/", admin.site.urls),
    path("", include("salas.urls")),
    path("reservas/", include("reservas.urls")),
    path("login/", auth_views.login_page, name="login_page"),
    path("api/auth/", include("auth_app.urls")),
]
