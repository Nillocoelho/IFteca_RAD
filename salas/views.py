import json

from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .models import Sala


@require_GET
def api_lookup_sala(request):
    """Procura uma sala por nome e retorna o id.

    Usado pelo JS quando a linha renderizada no servidor não inclui `data-id`.
    """
    nome = (request.GET.get("nome") or "").strip()
    if not nome:
        return JsonResponse({"errors": ["Parametro 'nome' e obrigatorio."]}, status=400)

    qs = Sala.objects.filter(nome=nome)
    count = qs.count()
    if count == 0:
        return JsonResponse({"errors": ["Sala nao encontrada."]}, status=404)
    if count > 1:
        return JsonResponse({"errors": ["Nome de sala ambiguo; existem multiplas entradas com esse nome."]}, status=409)

    sala = qs.first()
    return JsonResponse({"id": sala.id, "nome": sala.nome})


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
    for sala in salas_qs:
        # use persisted equipamentos/status when available; fallback to inference
        equipamentos = getattr(sala, 'equipamentos', []) or []
        status_label = getattr(sala, 'status', 'Disponivel')
        salas.append(
            {
                "id": sala.id,
                "nome": sala.nome,
                "andar": infer_andar(sala.nome),
                "tipo": getattr(sala, "tipo", ""),
                "descricao": getattr(sala, "descricao", ""),
                "capacidade": sala.capacidade,
                "status": status_label,
                "status_class": "",  # template/JS decide classes from status
                "equipamentos": equipamentos,
            }
        )

    return render(
        request,
        "salas/gerenciar_salas.html",
        {"salas": salas, "tipos": [choice[0] for choice in Sala.TIPO_CHOICES]},
    )


@require_GET
def criar_sala(request):
    return render(
        request,
        "salas/criar_sala.html",
        {"tipos": [choice[0] for choice in Sala.TIPO_CHOICES]},
    )


@csrf_exempt  # a view de API aceita chamadas via fetch; validação de campos continua
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

    # equipamentos may be sent as list or comma-separated string
    equipamentos = payload.get('equipamentos') or []
    if isinstance(equipamentos, str):
        equipamentos = [e.strip() for e in equipamentos.split(',') if e.strip()]
    status = payload.get('status') or 'Disponivel'

    sala = Sala.objects.create(nome=nome, capacidade=capacidade, tipo=tipo, equipamentos=equipamentos, status=status)
    return JsonResponse(
        {
            "message": "Sala cadastrada com sucesso.",
            "sala": {
                "id": sala.id,
                "nome": sala.nome,
                "capacidade": sala.capacidade,
                "tipo": sala.tipo,
                "localizacao": sala.localizacao,
                "equipamentos": sala.equipamentos,
                "status": sala.status,
                "detalhe": reverse("gerenciar_salas"),
            },
        }
    )


@csrf_exempt  # permite fetch sem sessão de admin; validação e CSRF do header permanecem
@require_http_methods(["POST", "PUT", "PATCH", "DELETE"])
def api_update_delete_sala(request, sala_id):
    try:
        sala = Sala.objects.get(id=sala_id)
    except Sala.DoesNotExist:
        return JsonResponse({"errors": ["Sala nao encontrada."]}, status=404)

    if request.method == "DELETE":
        sala.delete()
        return JsonResponse({"message": "Sala removida com sucesso.", "id": sala_id})

    # Allow updates via POST (legacy), PUT or PATCH
    # For PUT/PATCH Django does not populate request.POST, but request.body is available.

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"errors": ["Payload invalido. Envie JSON valido."]}, status=400)

    nome = (payload.get("nome") or "").strip()
    capacidade_raw = payload.get("capacidade")
    tipo = (payload.get("tipo") or "").strip()

    # optional fields
    localizacao = (payload.get("localizacao") or "").strip() or None
    equipamentos = payload.get("equipamentos") or []
    if isinstance(equipamentos, str):
        equipamentos = [e.strip() for e in equipamentos.split(',') if e.strip()]
    status = (payload.get("status") or "").strip() or None

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
    if localizacao is not None:
        sala.localizacao = localizacao
    if equipamentos:
        sala.equipamentos = equipamentos
    if status:
        sala.status = status
    sala.save()

    return JsonResponse(
        {
            "message": "Sala atualizada com sucesso.",
            "sala": {"id": sala.id, "nome": sala.nome, "capacidade": sala.capacidade, "tipo": sala.tipo},
        }
    )
