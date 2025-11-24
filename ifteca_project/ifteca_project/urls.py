"""
URL configuration for ifteca_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include  

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("reservas.urls")),
    path('salas/', include('salas.urls')),
    path('api/auth/', include('auth_app.urls')),
]
