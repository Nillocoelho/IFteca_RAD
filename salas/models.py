from django.db import models


class Sala(models.Model):
    TIPO_CHOICES = [
        ("Sala de Aula", "Sala de Aula"),
        ("Laboratorio", "Laboratorio"),
        ("Auditorio", "Auditorio"),
    ]

    nome = models.CharField(max_length=255)
    capacidade = models.PositiveIntegerField()
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    localizacao = models.CharField(max_length=255, blank=True, null=True, verbose_name='Localização (Bloco/Andar)')
    equipamentos = models.JSONField(default=list, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('Disponivel', 'Disponivel'), ('Ocupada', 'Ocupada'), ('Em Manutencao', 'Em Manutencao')],
        default='Disponivel',
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self) -> str:
        return f"{self.nome} ({self.tipo})"
