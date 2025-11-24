import json

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from .models import Sala


@require_GET
def gerenciar_salas(request):
    salas = Sala.objects.all()
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
