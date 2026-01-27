import logging
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

logger = logging.getLogger(__name__)


def _format_reserva(reserva):
    """Retorna tupla (data, inicio, fim) formatada para o email."""
    inicio_local = timezone.localtime(reserva.inicio)
    fim_local = timezone.localtime(reserva.fim)
    data = inicio_local.strftime("%d/%m/%Y")
    horario_inicio = inicio_local.strftime("%H:%M")
    horario_fim = fim_local.strftime("%H:%M")
    return data, horario_inicio, horario_fim


def _send_email(subject, body, destinatario=None):
    """Envia email usando o backend configurado no Django."""
    to_email = destinatario or getattr(
        settings,
        "RESERVA_EMAIL_DESTINO",
        "coelho.danillo@academico.ifpb.edu.br",
    )
    smtp_backend = "django.core.mail.backends.smtp.EmailBackend"
    if (
        getattr(settings, "EMAIL_BACKEND", smtp_backend) == smtp_backend
        and (not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD)
    ):
        logger.warning("Email SMTP nao configurado; pulando envio para %s", to_email)
        return
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    email.send(fail_silently=False)
    logger.info("Email enviado para %s: %s", to_email, subject)


def enviar_confirmacao(reserva, destinatario=None):
    """Dispara email de confirmacao de reserva."""
    data, inicio, fim = _format_reserva(reserva)
    subject = f"Confirmacao de Reserva: Sala {reserva.sala.nome}"
    body = (
        "Ola,\n\n"
        f"Sua reserva para a sala \"{reserva.sala.nome}\" foi confirmada.\n\n"
        "Detalhes:\n"
        f"- Data: {data}\n"
        f"- Horario: {inicio} - {fim}\n"
        f"- Usuario: {reserva.usuario}\n\n"
        "Obrigado por usar o sistema de agendamento."
    )
    _send_email(subject, body, destinatario)


def enviar_cancelamento(reserva, destinatario=None):
    """Dispara email de cancelamento de reserva."""
    data, inicio, fim = _format_reserva(reserva)
    subject = f"Cancelamento de Reserva: Sala {reserva.sala.nome}"
    body = (
        "Ola,\n\n"
        f"Sua reserva para a sala \"{reserva.sala.nome}\" foi cancelada.\n\n"
        "Detalhes:\n"
        f"- Data: {data}\n"
        f"- Horario: {inicio} - {fim}\n"
        f"- Usuario: {reserva.usuario}\n\n"
        "O horario voltou a ficar disponivel."
    )
    _send_email(subject, body, destinatario)
