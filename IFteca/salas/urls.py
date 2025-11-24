from django.urls import path
from . import views

urlpatterns = [
    path("", views.gerenciar_salas, name="gerenciar_salas"),
]
