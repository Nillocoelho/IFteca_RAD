import json

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .models import Sala


@require_GET
def gerenciar_salas(request):
    # Lista salas reais e complementa com dados de exibição (andar/status/equipamentos) para a UI.
    salas_qs = Sala.objects.all()

    def infer_andar(nome: str) -> str:
        nome = (nome or "").lower()
        if any(code in nome for code in ["101", "102", "103"]):
            return "1o Andar - Bloco A"
        if any(code in nome for code in ["201", "202", "203"]):
            return "2o Andar - Bloco B"
        return "1o Andar - Bloco A"

    status_map = {0: ("Disponivel", "success"), 1: ("Ocupada", "danger"), 2: ("Em Manutencao", "warning")}
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
        return JsonResponse({"errors": ["Payload invalido. Envie JSON valido."]}, status=400)

    nome = (payload.get("nome") or "").strip()
    capacidade_raw = payload.get("capacidade")
    tipo = (payload.get("tipo") or "").strip()

    errors = []

    if not nome:
        errors.append("O nome da sala e obrigatorio.")

    try:
        capacidade = int(capacidade_raw)
        if capacidade <= 0:
            raise ValueError
    except (TypeError, ValueError):
        errors.append("Capacidade deve ser um numero inteiro positivo.")
        capacidade = None

    tipos_validos = [choice[0] for choice in Sala.TIPO_CHOICES]
    if tipo not in tipos_validos:
        errors.append("Selecione um tipo de sala valido.")

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


@staff_member_required
@require_http_methods(["POST", "DELETE"])
def api_update_delete_sala(request, sala_id):
    try:
        sala = Sala.objects.get(id=sala_id)
    except Sala.DoesNotExist:
        return JsonResponse({"errors": ["Sala nao encontrada."]}, status=404)

    if request.method == "DELETE":
        sala.delete()
        return JsonResponse({"message": "Sala removida com sucesso.", "id": sala_id})

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"errors": ["Payload invalido. Envie JSON valido."]}, status=400)

    nome = (payload.get("nome") or "").strip()
    capacidade_raw = payload.get("capacidade")
    tipo = (payload.get("tipo") or "").strip()

    errors = []
    if not nome:
        errors.append("O nome da sala e obrigatorio.")

    try:
        capacidade = int(capacidade_raw)
        if capacidade <= 0:
            raise ValueError
    except (TypeError, ValueError):
        errors.append("Capacidade deve ser um numero inteiro positivo.")
        capacidade = None

    tipos_validos = [choice[0] for choice in Sala.TIPO_CHOICES]
    if tipo and tipo not in tipos_validos:
        errors.append("Selecione um tipo de sala valido.")

    if errors:
        return JsonResponse({"errors": errors}, status=400)

    sala.nome = nome or sala.nome
    if capacidade is not None:
        sala.capacidade = capacidade
    if tipo:
        sala.tipo = tipo
    sala.save()

    return JsonResponse(
        {
            "message": "Sala atualizada com sucesso.",
            "sala": {"id": sala.id, "nome": sala.nome, "capacidade": sala.capacidade, "tipo": sala.tipo},
        }
    )
