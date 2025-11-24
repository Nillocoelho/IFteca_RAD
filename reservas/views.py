import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Sala, Reserva


# ============================================
#  ENDPOINT ADMIN: LISTAR E CRIAR (GET/POST)
# ============================================

@csrf_exempt
def salas_admin(request):
    """
    Endpoint GET/POST /api/admin/salas/
    - GET: lista salas
    - POST: cria nova sala
    """

    # --------------- GET lista ---------------
    if request.method == "GET":
        salas = Sala.objects.all().order_by("nome")

        data = [
            {
                "id": s.id,
                "nome": s.nome,
                "capacidade": s.capacidade,
                "tipo": s.tipo,
                "localizacao": s.localizacao,
            }
            for s in salas
        ]
        return JsonResponse(data, safe=False, status=200)

    # --------------- POST cria ---------------
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"detail": "JSON inválido."}, status=400)

        required = ["nome", "capacidade", "tipo", "localizacao"]
        missing = [f for f in required if f not in data]
        if missing:
            return JsonResponse(
                {"detail": f"Campos obrigatórios faltando: {', '.join(missing)}"},
                status=400,
            )

        # Nome único
        if Sala.objects.filter(nome=data["nome"]).exists():
            return JsonResponse({"detail": "Já existe uma sala com esse nome."}, status=400)

        # Capacidade
        try:
            capacidade = int(data["capacidade"])
            if capacidade <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return JsonResponse(
                {"detail": "Capacidade deve ser um inteiro positivo."},
                status=400,
            )

        # Tipo
        tipos_validos = dict(Sala.TIPO_CHOICES).keys()
        if data["tipo"] not in tipos_validos:
            return JsonResponse(
                {"detail": "Tipo inválido. Valores aceitos: " + ", ".join(tipos_validos)},
                status=400,
            )

        sala = Sala.objects.create(
            nome=data["nome"],
            capacidade=capacidade,
            tipo=data["tipo"],
            localizacao=data["localizacao"],
        )

        return JsonResponse(
            {
                "id": sala.id,
                "nome": sala.nome,
                "capacidade": sala.capacidade,
                "tipo": sala.tipo,
                "localizacao": sala.localizacao,
            },
            status=201,
        )

    return JsonResponse({"detail": "Método não permitido."}, status=405)


# ============================================
#  ENDPOINT UPDATE (PUT)
# ============================================

@csrf_exempt
def atualizar_sala(request, sala_id):
    """
    Endpoint PUT /api/admin/salas/<id>/
    Atualiza dados de uma sala existente.
    """

    if request.method != "PUT":
        return JsonResponse({"detail": "Método não permitido."}, status=405)

    try:
        sala = Sala.objects.get(id=sala_id)
    except Sala.DoesNotExist:
        return JsonResponse({"detail": "Sala não encontrada."}, status=404)

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "JSON inválido."}, status=400)

    nome = data.get("nome", sala.nome)
    capacidade = data.get("capacidade", sala.capacidade)
    tipo = data.get("tipo", sala.tipo)
    localizacao = data.get("localizacao", sala.localizacao)

    # Nome duplicado
    if Sala.objects.filter(nome=nome).exclude(id=sala.id).exists():
        return JsonResponse(
            {"detail": "Já existe outra sala com esse nome."},
            status=400,
        )

    # Capacidade
    try:
        capacidade = int(capacidade)
        if capacidade <= 0:
            raise ValueError
    except (TypeError, ValueError):
        return JsonResponse({"detail": "Capacidade deve ser um inteiro positivo."}, status=400)

    # Tipo
    tipos_validos = dict(Sala.TIPO_CHOICES).keys()
    if tipo not in tipos_validos:
        return JsonResponse(
            {"detail": "Tipo inválido. Valores aceitos: " + ", ".join(tipos_validos)},
            status=400,
        )

    sala.nome = nome
    sala.capacidade = capacidade
    sala.tipo = tipo
    sala.localizacao = localizacao
    sala.save()

    return JsonResponse(
        {
            "id": sala.id,
            "nome": sala.nome,
            "capacidade": sala.capacidade,
            "tipo": sala.tipo,
            "localizacao": sala.localizacao,
        },
        status=200,
    )


# ============================================
#  ENDPOINT DELETE (com validação CA2)
# ============================================

@csrf_exempt
def deletar_sala(request, sala_id):
    """
    Endpoint DELETE /api/admin/salas/<id>/
    Exclui uma sala existente, validando reservas futuras.
    """

    if request.method != "DELETE":
        return JsonResponse({"detail": "Método não permitido."}, status=405)

    try:
        sala = Sala.objects.get(id=sala_id)
    except Sala.DoesNotExist:
        return JsonResponse({"detail": "Sala não encontrada."}, status=404)

    # CA2 — regra crítica: bloquear exclusão se houver reservas futuras
    if Reserva.objects.filter(sala=sala, data__gt=models.functions.Now()).exists():
        return JsonResponse(
            {"detail": "A sala possui reservas futuras e não pode ser excluída."},
            status=400,
        )

    sala.delete()

    return JsonResponse({"detail": "Sala excluída com sucesso."}, status=200)


# ============================================
#  ENDPOINT PÚBLICO (GET)
# ============================================

def salas_publicas(request):
    """
    Endpoint GET /api/salas/publicas
    """
    if request.method != "GET":
        return JsonResponse({"detail": "Método não permitido."}, status=405)

    salas = Sala.objects.all().order_by("nome")

    data = [
        {
            "nome": s.nome,
            "capacidade": s.capacidade,
            "tipo": s.tipo,
        }
        for s in salas
    ]

    return JsonResponse(data, safe=False, status=200)


def gerenciar_salas_ui(request):
    """Renderiza a interface de gerenciamento de salas (mock admin sem login por enquanto)."""
    tipos = Sala.TIPO_CHOICES
    return render(request, 'reservas/gerenciar_salas.html', {'tipos': tipos})


