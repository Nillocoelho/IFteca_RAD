from django.urls import path

from . import views

urlpatterns = [
    # ÁREA ADMIN
    path("admin/salas/", views.gerenciar_salas, name="gerenciar_salas"),
    path("admin/salas/novo", views.criar_sala, name="criar_sala"),
    # APIs protegidas
    path("api/salas/", views.api_criar_sala, name="api_criar_sala"),
    path("api/salas/lookup/", views.api_lookup_sala, name="api_lookup_sala"),
    path("api/salas/<int:sala_id>/", views.api_update_delete_sala, name="api_update_delete_sala"),
]
