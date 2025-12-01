# reservas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Admin
    path("admin/salas/", views.salas_admin, name="salas_admin"),
    path("admin/salas/<int:sala_id>/", views.atualizar_sala, name="atualizar_sala"),
    path("admin/salas/<int:sala_id>/delete/", views.deletar_sala, name="deletar_sala"),
    path("admin/salas/manage/", views.gerenciar_salas_ui, name="gerenciar_salas_ui"),

    # Estudantes
    path("minhas-reservas/", views.minhas_reservas, name="minhas_reservas"),
    path("confirmacao-reserva/", views.confirmacao_reserva, name="confirmacao_reserva"),

    # Público
    path("salas/publicas/", views.salas_publicas, name="salas_publicas"),
]


