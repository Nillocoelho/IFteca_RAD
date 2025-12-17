from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Sala(models.Model):
    TIPO_CHOICES = [("Coletiva", "Coletiva"), ("Auditorio", "Auditorio")]

    nome = models.CharField(max_length=255)
    capacidade = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    localizacao = models.CharField(max_length=255, blank=True, null=True, verbose_name="Localizacao")
    equipamentos = models.JSONField(default=list, blank=True)
    descricao = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[("Disponivel", "Disponivel"), ("Em Manutencao", "Em Manutencao")],
        default="Disponivel",
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Indica se a sala está ativa no sistema. Salas inativas não aparecem para usuários.",
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(
                fields=['nome'],
                condition=models.Q(ativo=True),
                name='unique_nome_sala_ativa'
            )
        ]

    def __str__(self) -> str:
        return f"{self.nome} ({self.tipo})"

    def clean(self):
        # trim strings
        if isinstance(self.nome, str):
            self.nome = self.nome.strip()
        if isinstance(self.localizacao, str):
            self.localizacao = self.localizacao.strip() or None
        if isinstance(self.descricao, str):
            self.descricao = self.descricao.strip() or None

        # capacidade ja validada por MinValueValidator; reforco aqui
        if self.capacidade is not None and self.capacidade <= 0:
            raise ValidationError({"capacidade": "Capacidade deve ser maior que zero."})

        # valida equipamentos: precisa ser lista de strings nao vazias
        if self.equipamentos is None:
            self.equipamentos = []
        if not isinstance(self.equipamentos, list):
            raise ValidationError({"equipamentos": "Equipamentos deve ser uma lista."})
        cleaned_equip = []
        for item in self.equipamentos:
            if not isinstance(item, str):
                raise ValidationError({"equipamentos": "Cada equipamento deve ser texto."})
            item = item.strip()
            if item:
                cleaned_equip.append(item)
        self.equipamentos = cleaned_equip
