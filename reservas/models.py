from django.db import models
from django.utils import timezone


# Agora usamos o modelo canônico `salas.Sala` para evitar duplicação.
# A migration criada atualiza os FKs e remove o modelo duplicado em `reservas`.
class Reserva(models.Model):
    sala = models.ForeignKey(
        'salas.Sala',
        on_delete=models.CASCADE,
        related_name="reservas",
    )

    usuario = models.CharField(
        max_length=100,
        verbose_name="Usuário",
    )

    inicio = models.DateTimeField(
        verbose_name="Início da Reserva",
    )

    fim = models.DateTimeField(
        verbose_name="Fim da Reserva",
    )

    def __str__(self):
        return f"Reserva da sala {self.sala.nome} em {self.inicio.strftime('%d/%m/%Y %H:%M')}"

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ["inicio"]
