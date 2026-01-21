# reservas/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Dashboard Admin
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("api/dashboard/", views.api_dashboard_data, name="api_dashboard_data"),
    
    # Admin
    path("admin/salas/", views.salas_admin, name="salas_admin"),
    path("admin/salas/<int:sala_id>/", views.atualizar_sala, name="atualizar_sala"),
    path("admin/salas/<int:sala_id>/delete/", views.deletar_sala, name="deletar_sala"),
    path("admin/salas/manage/", views.gerenciar_salas_ui, name="gerenciar_salas_ui"),
    path("admin/reserva/", views.admin_reservas, name="admin_reservas"),
    
    # Gerenciar Usuários (Admin)
    path("admin/usuarios/", views.gerenciar_usuarios, name="gerenciar_usuarios"),
    path("admin/usuarios/<int:usuario_id>/toggle/", views.api_toggle_usuario, name="api_toggle_usuario"),

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


