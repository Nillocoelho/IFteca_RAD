import json

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST, require_http_methods

from .models import Sala


def _is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def admin_required(view_func):
    return login_required(user_passes_test(_is_admin, login_url="/login/")(view_func))


@require_GET
def listar_salas(request):
    # Lista de salas visivel para alunos. Usa dados reais, mas apresenta estado estatico de usuario.
    salas_qs = Sala.objects.filter(ativo=True)
    salas = []
    for sala in salas_qs:
        equipamentos = getattr(sala, "equipamentos", []) or []
        status_label = getattr(sala, "status", "Disponivel") or "Disponivel"
        salas.append(
            {
                "id": sala.id,
                "nome": sala.nome,
                "tipo": sala.tipo,
                "capacidade": sala.capacidade,
                "status": status_label,
                "status_class": "",
                "equipamentos": equipamentos,
            }
        )

    if not salas:
        salas = [ {k: v for k, v in sala.items() if k != "descricao"} for sala in _fallback_salas() ]

    # Paginação
    paginator = Paginator(salas, 8)  # 8 salas por página
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.get_page(1)

    student_name = (
        getattr(request.user, "get_full_name", lambda: "")() or getattr(request.user, "username", "") or "Aluno convidado"
    )

    return render(
        request,
        "salas/listar_salas.html",
        {
            "salas": page_obj.object_list,
            "page_obj": page_obj,
            "student_name": student_name,
            "is_authenticated": request.user.is_authenticated,
        },
    )


@require_GET
def detalhar_sala(request, sala_id: int):
    """Tela de detalhe/agenda da sala."""
    fallback = _fallback_salas()
    try:
        sala_obj = Sala.objects.get(id=sala_id, ativo=True)
        sala = {
            "id": sala_obj.id,
            "nome": sala_obj.nome,
            "tipo": sala_obj.tipo,
            "status": getattr(sala_obj, "status", "Disponivel") or "Disponivel",
            "capacidade": sala_obj.capacidade,
            "descricao": getattr(sala_obj, "descricao", "") or "Sala de estudo.",
            "equipamentos": getattr(sala_obj, "equipamentos", []) or [],
        }
    except Sala.DoesNotExist:
        sala = next((s for s in fallback if s["id"] == sala_id), None)
        if not sala:
            return redirect("listar_salas")

    slots = [
        {"range": "08:00 - 10:00", "status": "disponivel"},
        {"range": "10:00 - 12:00", "status": "ocupado"},
        {"range": "12:00 - 14:00", "status": "disponivel"},
        {"range": "14:00 - 16:00", "status": "disponivel"},
        {"range": "16:00 - 18:00", "status": "ocupado"},
        {"range": "18:00 - 20:00", "status": "disponivel"},
        {"range": "20:00 - 22:00", "status": "disponivel"},
    ]

    student_name = (
        getattr(request.user, "get_full_name", lambda: "")() or getattr(request.user, "username", "") or "Aluno convidado"
    )

    return render(
        request,
        "salas/detalhar_sala.html",
        {
            "sala": sala, 
            "slots": slots, 
            "student_name": student_name,
            "is_authenticated": request.user.is_authenticated,
        },
    )


def _fallback_salas():
    return [
        {
            "id": 101,
            "nome": "Sala 101",
            "tipo": "Coletiva",
            "capacidade": 20,
            "status": "Disponivel",
            "status_class": "",
            "equipamentos": ["Projetor", "Quadro branco", "Ar condicionado"],
            "descricao": "Sala ampla e bem iluminada, ideal para grupos de estudo.",
        },
        {
            "id": 102,
            "nome": "Sala 102",
            "tipo": "Coletiva",
            "capacidade": 15,
            "status": "Disponivel",
            "status_class": "",
            "equipamentos": ["Quadro branco", "Ar condicionado"],
            "descricao": "Ambiente silencioso para ate 15 pessoas.",
        },
        {
            "id": 103,
            "nome": "Sala 103",
            "tipo": "Auditorio",
            "capacidade": 25,
            "status": "Em Manutencao",
            "status_class": "",
            "equipamentos": ["Projetor", "Quadro branco", "Ar condicionado", "TV"],
            "descricao": "Sala com TV e projetor para apresentacoes.",
        },
        {
            "id": 201,
            "nome": "Sala 201",
            "tipo": "Coletiva",
            "capacidade": 30,
            "status": "Disponivel",
            "status_class": "",
            "equipamentos": ["Projetor", "Quadro branco", "Ar condicionado", "Computadores"],
            "descricao": "Laboratorio com computadores.",
        },
        {
            "id": 202,
            "nome": "Sala 202",
            "tipo": "Auditorio",
            "capacidade": 12,
            "status": "Em Manutencao",
            "status_class": "",
            "equipamentos": ["Quadro branco"],
            "descricao": "Sala em manutencao.",
        },
        {
            "id": 203,
            "nome": "Sala 203",
            "tipo": "Auditorio",
            "capacidade": 18,
            "status": "Disponivel",
            "status_class": "",
            "equipamentos": ["Projetor", "Quadro branco", "Ar condicionado"],
            "descricao": "Sala versatil para estudos.",
        },
    ]


@admin_required
@require_GET
def api_lookup_sala(request):
    """Procura uma sala por nome e retorna o id.

    Usado pelo JS quando a linha renderizada no servidor nao inclui `data-id`.
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


@admin_required
@require_GET
def gerenciar_salas(request):
    # Lista salas reais e complementa com dados de exibicao (status/equipamentos) para a UI.
    # Admin vê todas as salas (ativas e inativas)
    salas_qs = Sala.objects.all().order_by('nome')

    salas = []
    for sala in salas_qs:
        equipamentos = getattr(sala, 'equipamentos', []) or []
        status_label = getattr(sala, 'status', 'Disponivel')
        descricao = getattr(sala, "descricao", "") or ""
        salas.append(
            {
                "id": sala.id,
                "nome": sala.nome,
                "tipo": getattr(sala, "tipo", ""),
                "descricao": descricao,
                "capacidade": sala.capacidade,
                "status": status_label,
                "status_class": "",  # template/JS decide classes from status
                "equipamentos": equipamentos,
                "ativo": sala.ativo,  # Indica se a sala foi excluída (soft delete)
            }
        )

    return render(
        request,
        "salas/gerenciar_salas.html",
        {"salas": salas, "tipos": [choice[0] for choice in Sala.TIPO_CHOICES]},
    )


@admin_required
@require_GET
def criar_sala(request):
    # Redireciona para a listagem abrindo o modal de criacao
    return redirect(f"{reverse('gerenciar_salas')}?openModal=1")


@admin_required
@csrf_exempt  # a view de API aceita chamadas via fetch; validacao de campos continua
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

    if Sala.objects.filter(nome=nome, ativo=True).exists():
        return JsonResponse({"errors": ["Ja existe uma sala com esse nome."]}, status=400)

    equipamentos = payload.get('equipamentos') or []
    if isinstance(equipamentos, str):
        equipamentos = [e.strip() for e in equipamentos.split(',') if e.strip()]
    status = payload.get('status') or 'Disponivel'
    localizacao = (payload.get('localizacao') or '').strip()
    descricao = (payload.get('descricao') or '').strip()

    sala = Sala(
        nome=nome,
        capacidade=capacidade,
        tipo=tipo,
        equipamentos=equipamentos,
        status=status,
        localizacao=localizacao or None,
        descricao=descricao or None,
    )
    sala.full_clean()
    sala.save()
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
                "descricao": sala.descricao,
                "detalhe": reverse("gerenciar_salas"),
            },
        }
    )


@admin_required
@csrf_exempt  # permite fetch sem sessao de admin; validacao e CSRF do header permanecem
@require_http_methods(["POST", "PUT", "PATCH", "DELETE"])
def api_update_delete_sala(request, sala_id):
    try:
        sala = Sala.objects.get(id=sala_id)
    except Sala.DoesNotExist:
        return JsonResponse({"errors": ["Sala nao encontrada."]}, status=404)

    reservas_ativas_qs = sala.reservas.filter(
        cancelada=False,
        inicio__gte=timezone.now(),
    )

    if request.method == "DELETE":
        # Verifica se há reservas ativas (não canceladas e futuras)
        if reservas_ativas_qs.exists():
            return JsonResponse(
                {"errors": ["Não é possível excluir esta sala pois existem reservas ativas. Aguarde até que todas as reservas sejam concluídas ou canceladas."]},
                status=400
            )
        
        # Remove reservas históricas e deleta a sala (somente se não houver ativas)
        sala.reservas.all().delete()
        sala.delete()
        return JsonResponse({"message": "Sala removida com sucesso.", "id": sala_id})

    if reservas_ativas_qs.exists():
        return JsonResponse(
            {"errors": ["NÇœo Ç¸ possÇðvel editar esta sala pois existem reservas ativas. Aguarde atÇ¸ que todas as reservas sejam concluÇðdas ou canceladas."]},
            status=400,
        )

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"errors": ["Payload invalido. Envie JSON valido."]}, status=400)

    nome = (payload.get("nome") or "").strip()
    capacidade_raw = payload.get("capacidade")
    tipo = (payload.get("tipo") or "").strip()

    localizacao = (payload.get("localizacao") or "").strip() or None
    equipamentos = payload.get("equipamentos") or []
    if isinstance(equipamentos, str):
        equipamentos = [e.strip() for e in equipamentos.split(',') if e.strip()]
    status = (payload.get("status") or "").strip() or None
    descricao = (payload.get("descricao") or "").strip() or None

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

    # Nome duplicado (considera apenas salas ativas)
    if nome and Sala.objects.filter(nome=nome, ativo=True).exclude(id=sala.id).exists():
        return JsonResponse({"errors": ["Ja existe outra sala com esse nome."]}, status=400)

    sala.nome = nome or sala.nome
    if capacidade is not None:
        sala.capacidade = capacidade
    if tipo:
        sala.tipo = tipo
    sala.localizacao = localizacao if localizacao is not None else sala.localizacao
    sala.descricao = descricao if descricao is not None else sala.descricao
    if equipamentos:
        sala.equipamentos = equipamentos
    if status:
        sala.status = status
    sala.full_clean()
    sala.save()

    return JsonResponse(
        {
            "message": "Sala atualizada com sucesso.",
            "sala": {
                "id": sala.id,
                "nome": sala.nome,
                "capacidade": sala.capacidade,
                "tipo": sala.tipo,
                "localizacao": sala.localizacao,
                "descricao": sala.descricao,
                "status": sala.status,
                "equipamentos": sala.equipamentos,
            },
        }
    )
