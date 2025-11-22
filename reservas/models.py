from django.db import models
from django.utils import timezone


class Sala(models.Model):
    TIPO_CHOICES = [
        ('ESTUDO_INDIVIDUAL', 'Estudo Individual'),
        ('ESTUDO_GRUPO', 'Estudo em Grupo'),
        ('LABORATORIO', 'Laboratório'),
        ('SALA_AULA', 'Sala de Aula'),
    ]

    nome = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nome da Sala'
    )

    capacidade = models.PositiveIntegerField(
        default=1,
        verbose_name='Capacidade Máxima'
    )

    tipo = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        default='ESTUDO_GRUPO',
        verbose_name='Tipo de Sala'
    )

    localizacao = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Localização (Bloco/Andar)'
    )

    def has_future_reservas(self):
        """
        CA2 – Verifica se a sala possui reservas futuras para bloquear exclusão.
        Usa related_name="reservas".
        """
        now = timezone.now()
        return self.reservas.filter(inicio__gte=now).exists()

    def __str__(self):
        return f"{self.nome} - Capacidade: {self.capacidade}"

    class Meta:
        verbose_name = 'Sala'
        verbose_name_plural = 'Salas'
        ordering = ['nome']


class Reserva(models.Model):
    sala = models.ForeignKey(
        Sala,
        on_delete=models.CASCADE,
        related_name="reservas"
    )

    usuario = models.CharField(
        max_length=100,
        verbose_name="Usuário"
    )

    inicio = models.DateTimeField(
        verbose_name="Início da Reserva"
    )

    fim = models.DateTimeField(
        verbose_name="Fim da Reserva"
    )

    def __str__(self):
        return f"Reserva da sala {self.sala.nome} em {self.inicio.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['inicio']
