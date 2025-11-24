from django.urls import path
from . import views

urlpatterns = [
    path("", views.gerenciar_salas, name="gerenciar_salas"),
    path("api/salas/", views.api_criar_sala, name="api_criar_sala"),
    path("api/salas/<int:sala_id>/", views.api_update_delete_sala, name="api_update_delete_sala"),
]
