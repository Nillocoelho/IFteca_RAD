import json

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from .models import Sala


@require_GET
def gerenciar_salas(request):
    # Monta uma lista de dicionários com campos de exibição adicionais
    salas_qs = Sala.objects.all()

    def infer_andar(nome):
        nome = (nome or "").lower()
        if any(code in nome for code in ["101", "102", "103"]):
            return "1º Andar - Bloco A"
        if any(code in nome for code in ["201", "202", "203"]):
            return "2º Andar - Bloco B"
        return "1º Andar - Bloco A"

    status_map = {0: ("Disponível", "success"), 1: ("Ocupada", "danger"), 2: ("Em Manutenção", "warning")}
    equipamentos_choices = [
        ["Projetor", "Quadro branco"],
        ["Quadro branco", "Ar condicionado"],
        ["Projetor", "Quadro branco", "Microfone"],
    ]

    salas = []
    for i, sala in enumerate(salas_qs):
        status_label, status_class = status_map[i % 3]
        equipamentos = equipamentos_choices[i % len(equipamentos_choices)]
        salas.append(
            {
                "id": sala.id,
                "nome": sala.nome,
                "andar": infer_andar(sala.nome),
                "capacidade": sala.capacidade,
                "status": status_label,
                "status_class": status_class,
                "equipamentos": equipamentos,
            }
        )

    return render(
        request,
        "salas/gerenciar_salas.html",
        {"salas": salas, "tipos": [choice[0] for choice in Sala.TIPO_CHOICES]},
    )


@staff_member_required
@require_GET
def criar_sala(request):
    return render(
        request,
        "salas/criar_sala.html",
        {"tipos": [choice[0] for choice in Sala.TIPO_CHOICES]},
    )


@staff_member_required
@require_POST
def api_criar_sala(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"errors": ["Payload inválido. Envie JSON válido."]}, status=400)

    nome = (payload.get("nome") or "").strip()
    capacidade_raw = payload.get("capacidade")
    tipo = (payload.get("tipo") or "").strip()

    errors = []

    if not nome:
        errors.append("O nome da sala é obrigatório.")

    try:
        capacidade = int(capacidade_raw)
        if capacidade <= 0:
            raise ValueError
    except (TypeError, ValueError):
        errors.append("Capacidade deve ser um número inteiro positivo.")
        capacidade = None

    tipos_validos = [choice[0] for choice in Sala.TIPO_CHOICES]
    if tipo not in tipos_validos:
        errors.append("Selecione um tipo de sala válido.")

    if errors:
        return JsonResponse({"errors": errors}, status=400)

    sala = Sala.objects.create(nome=nome, capacidade=capacidade, tipo=tipo)
    return JsonResponse(
        {
            "message": "Sala cadastrada com sucesso.",
            "sala": {
                "id": sala.id,
                "nome": sala.nome,
                "capacidade": sala.capacidade,
                "tipo": sala.tipo,
                "detalhe": reverse("gerenciar_salas"),
            },
        }
    )
