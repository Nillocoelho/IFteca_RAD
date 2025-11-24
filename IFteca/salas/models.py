from django.db import models


class Sala(models.Model):
    TIPO_CHOICES = [
        ("Sala de Aula", "Sala de Aula"),
        ("Laboratório", "Laboratório"),
        ("Auditório", "Auditório"),
    ]

    nome = models.CharField(max_length=255)
    capacidade = models.PositiveIntegerField()
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.tipo})"
