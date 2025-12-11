# reservas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Admin
    path("admin/salas/", views.salas_admin, name="salas_admin"),
    path("admin/salas/<int:sala_id>/", views.atualizar_sala, name="atualizar_sala"),
    path("admin/salas/<int:sala_id>/delete/", views.deletar_sala, name="deletar_sala"),
    path("admin/salas/manage/", views.gerenciar_salas_ui, name="gerenciar_salas_ui"),
    path("admin/reserva/", views.admin_reservas, name="admin_reservas"),

    # Estudantes
    path("minhas-reservas/", views.minhas_reservas, name="minhas_reservas"),
    path("confirmacao-reserva/", views.confirmacao_reserva, name="confirmacao_reserva"),
    path("reserva/<int:reserva_id>/", views.detalhes_reserva, name="detalhes_reserva"),

    # API
    path("api/reservas/<int:reserva_id>/cancelar/", views.api_cancelar_reserva, name="api_cancelar_reserva"),
    path("admin/reservas/<int:reserva_id>/cancelar/", views.api_admin_cancel_reserva, name="api_admin_cancel_reserva"),

    # Público
    path("salas/publicas/", views.salas_publicas, name="salas_publicas"),
]


