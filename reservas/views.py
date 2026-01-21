import json
import logging
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import models
from django.db.models import Count
from django.db.models.functions import TruncMonth

# Use the canonical Sala model from the `salas` app to avoid duplication
from salas.models import Sala
from .models import Reserva
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


# ============================================
#  ENDPOINT ADMIN: LISTAR E CRIAR (GET/POST)
# ============================================

@login_required(login_url="/login/")
@csrf_exempt
def salas_admin(request):
    """
    Endpoint GET/POST /api/admin/salas/
    - GET: lista salas (paginado, 8 por página)
    - POST: cria nova sala
    """

    # --------------- GET lista ---------------
    if request.method == "GET":
        logger.info("salas_admin GET recebido")
        # Admin vê todas as salas, mas filtra apenas as ativas
        salas = Sala.objects.filter(ativo=True).order_by("nome")
        
        # Paginação
        page_number = request.GET.get('page', 1)
        paginator = Paginator(salas, 8)  # 8 salas por página
        
        try:
            page_obj = paginator.get_page(page_number)
        except (EmptyPage, PageNotAnInteger):
            page_obj = paginator.get_page(1)

        data = [
            {
                "id": s.id,
                "nome": s.nome,
                "capacidade": s.capacidade,
                "tipo": s.tipo,
                "localizacao": s.localizacao,
                "equipamentos": getattr(s, 'equipamentos', []),
                "status": getattr(s, 'status', 'Disponivel'),
                "ativo": s.ativo,  # Incluído para futuras funcionalidades
                "descricao": getattr(s, 'descricao', '') or "",
            }
            for s in page_obj
        ]
        
        response_data = {
            "salas": data,
            "pagination": {
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
            }
        }
        
        logger.info("salas_admin GET retornando página %s de %s (%s salas)", 
                    page_obj.number, paginator.num_pages, len(data))
        return JsonResponse(response_data, safe=False, status=200)

    # --------------- POST cria ---------------
    if request.method == "POST":
        # Apenas superusuários podem criar salas
        if not request.user.is_superuser:
            return JsonResponse({"detail": "Apenas administradores podem criar salas."}, status=403)
        
        try:
            raw_body = request.body.decode("utf-8")
            logger.info("salas_admin POST recebido com body cru: %s", raw_body)
            data = json.loads(raw_body)
        except json.JSONDecodeError:
            logger.warning("salas_admin POST com JSON inválido", exc_info=True)
            return JsonResponse({"detail": "JSON inválido."}, status=400)

        required = ["nome", "capacidade", "tipo"]
        missing = [f for f in required if f not in data]
        if missing:
            logger.warning("salas_admin POST faltando campos obrigatórios: %s", missing)
            return JsonResponse(
                {"detail": f"Campos obrigatórios faltando: {', '.join(missing)}"},
                status=400,
            )

        # Nome único (considera apenas salas ativas)
        if Sala.objects.filter(nome=data["nome"], ativo=True).exists():
            logger.warning("salas_admin POST duplicado para nome='%s'", data["nome"])
            return JsonResponse({"detail": "Já existe uma sala com esse nome."}, status=400)

        # Capacidade
        try:
            capacidade = int(data["capacidade"])
            if capacidade <= 0:
                raise ValueError
        except (TypeError, ValueError):
            logger.warning("salas_admin POST capacidade inválida: %s", data.get("capacidade"))
            return JsonResponse(
                {"detail": "Capacidade deve ser um inteiro positivo."},
                status=400,
            )

        # Tipo
        tipos_validos = dict(Sala.TIPO_CHOICES).keys()
        if data["tipo"] not in tipos_validos:
            logger.warning("salas_admin POST tipo inválido: %s", data["tipo"])
            return JsonResponse(
                {"detail": "Tipo inválido. Valores aceitos: " + ", ".join(tipos_validos)},
                status=400,
            )

        # Localização (opcional)
        localizacao = data.get("localizacao")

        equipamentos = data.get('equipamentos') or []
        if isinstance(equipamentos, str):
            equipamentos = [e.strip() for e in equipamentos.split(',') if e.strip()]
        status = data.get('status') or 'Disponivel'
        descricao = data.get('descricao', '')

        sala = Sala.objects.create(
            nome=data["nome"],
            capacidade=capacidade,
            tipo=data["tipo"],
            localizacao=localizacao,
            equipamentos=equipamentos,
            status=status,
            descricao=descricao,
        )

        logger.info(
            "sala criada com sucesso id=%s nome='%s' capacidade=%s tipo=%s",
            sala.id,
            sala.nome,
            sala.capacidade,
            sala.tipo,
        )
        return JsonResponse(
            {
                "id": sala.id,
                "nome": sala.nome,
                "capacidade": sala.capacidade,
                "tipo": sala.tipo,
                "localizacao": sala.localizacao,
                "equipamentos": sala.equipamentos,
                "descricao": sala.descricao,
            },
            status=201,
        )

    return JsonResponse({"detail": "Método não permitido."}, status=405)


# ============================================
#  ENDPOINT UPDATE (PUT)
# ============================================

@login_required(login_url="/login/")
@csrf_exempt
def atualizar_sala(request, sala_id):
    """
    Endpoint PUT /api/admin/salas/<id>/
    Atualiza dados de uma sala existente.
    """

    if request.method != "PUT":
        return JsonResponse({"detail": "Método não permitido."}, status=405)

    # Apenas superusuários podem editar salas
    if not request.user.is_superuser:
        return JsonResponse({"detail": "Apenas administradores podem editar salas."}, status=403)

    try:
        sala = Sala.objects.get(id=sala_id)
    except Sala.DoesNotExist:
        return JsonResponse({"detail": "Sala não encontrada."}, status=404)

    reservas_ativas = Reserva.objects.filter(
        sala=sala,
        cancelada=False,
        inicio__gt=timezone.now(),
    ).exists()

    if reservas_ativas:
        return JsonResponse(
            {"detail": "A sala possui reservas futuras e não pode ser editada."},
            status=400,
        )

    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "JSON inválido."}, status=400)

    nome = data.get("nome", sala.nome)
    capacidade = data.get("capacidade", sala.capacidade)
    tipo = data.get("tipo", sala.tipo)

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

    # Equipamentos e descrição
    equipamentos = data.get('equipamentos', sala.equipamentos)
    if isinstance(equipamentos, str):
        equipamentos = [e.strip() for e in equipamentos.split(',') if e.strip()]
    descricao = data.get('descricao', sala.descricao)

    sala.nome = nome
    sala.capacidade = capacidade
    sala.tipo = tipo
    sala.equipamentos = equipamentos
    sala.descricao = descricao
    sala.save()

    return JsonResponse(
        {
            "id": sala.id,
            "nome": sala.nome,
            "capacidade": sala.capacidade,
            "tipo": sala.tipo,
            "localizacao": sala.localizacao,
            "equipamentos": sala.equipamentos,
            "descricao": sala.descricao,
        },
        status=200,
    )


# ============================================
#  ENDPOINT DELETE (com validação CA2)
# ============================================

@login_required(login_url="/login/")
@csrf_exempt
def deletar_sala(request, sala_id):
    """
    Endpoint DELETE /api/admin/salas/<id>/
    Exclui uma sala existente, validando reservas futuras.
    """

    if request.method != "DELETE":
        return JsonResponse({"detail": "Método não permitido."}, status=405)

    # Apenas superusuários podem excluir salas
    if not request.user.is_superuser:
        return JsonResponse({"detail": "Apenas administradores podem excluir salas."}, status=403)

    try:
        sala = Sala.objects.get(id=sala_id)
    except Sala.DoesNotExist:
        return JsonResponse({"detail": "Sala não encontrada."}, status=404)

    # CA2 — regra crítica: bloquear exclusão se houver reservas futuras (não canceladas)
    reservas_futuras = Reserva.objects.filter(
        sala=sala,
        cancelada=False,
        inicio__gt=timezone.now()
    ).exists()
    
    if reservas_futuras:
        return JsonResponse(
            {"detail": "A sala possui reservas futuras e não pode ser excluída."},
            status=400,
        )

    # Remove reservas passadas/canceladas e a própria sala
    Reserva.objects.filter(sala=sala).delete()
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


@login_required(login_url="/login/")
def gerenciar_salas_ui(request):
    """Renderiza a interface de gerenciamento de salas (mock admin sem login por enquanto)."""
    tipos = Sala.TIPO_CHOICES
    # Apenas superusuários podem editar/remover
    is_admin = request.user.is_superuser
    return render(request, 'reservas/gerenciar_salas.html', {'tipos': tipos, 'is_admin': is_admin})


@login_required(login_url="/login/")
def minhas_reservas(request):
    """
    Renderiza a tela de 'Minhas Reservas' para estudantes.
    Mostra as reservas ativas e anteriores do usuário logado.
    
    IMPORTANTE: select_related('sala') garante que salas inativas (soft delete)
    ainda sejam exibidas no histórico de reservas.
    """
    usuario = request.user.username
    agora = timezone.now()
    
    # Reservas ativas (futuras e não canceladas)
    reservas_ativas = Reserva.objects.filter(
        usuario=usuario,
        fim__gte=agora,
        cancelada=False
    ).select_related('sala').order_by('inicio')
    
    # Reservas anteriores (já concluídas ou canceladas)
    # NOTA: Mesmo salas deletadas (ativo=False) aparecem aqui via ForeignKey
    reservas_anteriores_qs = Reserva.objects.filter(
        usuario=usuario
    ).filter(
        models.Q(fim__lt=agora) | models.Q(cancelada=True)
    ).select_related('sala').order_by('-inicio')
    
    # Paginação para reservas anteriores
    paginator = Paginator(reservas_anteriores_qs, 8)  # 8 reservas por página
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.get_page(1)
    
    # Total de reservas
    total_reservas = Reserva.objects.filter(usuario=usuario).count()
    
    context = {
        'reservas_ativas': reservas_ativas,
        'reservas_anteriores': page_obj.object_list,
        'page_obj': page_obj,
        'total_reservas': total_reservas,
    }
    
    return render(request, 'reservas/minhas_reservas.html', context)


@login_required(login_url="/login/")
def confirmacao_reserva(request):
    """Renderiza a tela de confirmação de reserva."""
    return render(request, 'reservas/confirmacao_reserva.html')


@login_required(login_url="/login/")
def detalhes_reserva(request, reserva_id):
    """Renderiza a tela de detalhes de uma reserva específica."""
    try:
        reserva = Reserva.objects.get(id=reserva_id, usuario=request.user.username)
    except Reserva.DoesNotExist:
        return render(request, '404.html', status=404)
    
    # Determina o status da reserva
    agora = timezone.now()
    if reserva.cancelada:
        status = 'Cancelada'
    elif reserva.fim < agora:
        status = 'Concluída'
    else:
        status = 'Ativa'
    
    context = {
        'reserva': reserva,
        'status': status,
    }
    return render(request, 'reservas/detalhes_reserva.html', context)


@staff_member_required(login_url='/login/')
def admin_reservas(request):
    """Renderiza a interface administrativa de gerenciamento de reservas.
    Suporta filtros por sala (`sala` query param) e por data (`data` YYYY-MM-DD).
    """
    salas = Sala.objects.all().order_by('nome')
    reservas = Reserva.objects.select_related('sala').all().order_by('-inicio')

    # Filtros via query params
    sala_id = request.GET.get('sala')
    data_str = request.GET.get('data')
    if sala_id:
        try:
            reservas = reservas.filter(sala__id=int(sala_id))
        except (ValueError, TypeError):
            pass
    if data_str:
        try:
            from datetime import datetime as _dt
            data_filter = _dt.strptime(data_str, '%Y-%m-%d').date()
            reservas = reservas.filter(inicio__date=data_filter)
        except ValueError:
            pass

    # Estatísticas
    agora = timezone.now()
    total = Reserva.objects.count()
    ativos = Reserva.objects.filter(fim__gte=agora, cancelada=False).count()
    concluidos = Reserva.objects.filter(fim__lt=agora, cancelada=False).count()
    canceladas = Reserva.objects.filter(cancelada=True).count()

    # Enrich reservas with user info
    reservas_enriched = []
    for r in reservas:
        usuario_obj = User.objects.filter(username=r.usuario).first()
        full_name = usuario_obj.get_full_name() if usuario_obj and (usuario_obj.first_name or usuario_obj.last_name) else r.usuario
        email = usuario_obj.email if usuario_obj else ''
        criada_em = getattr(r, 'created_at', None) or r.inicio
        reservas_enriched.append({
            'obj': r,
            'usuario_nome': full_name,
            'usuario_email': email,
            'criada_em': criada_em,
        })

    # Paginação
    paginator = Paginator(reservas_enriched, 8)  # 8 reservas por página
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.get_page(1)

    # Apenas superusuários podem cancelar reservas
    is_admin = request.user.is_superuser
    
    context = {
        'salas': salas,
        'reservas': page_obj.object_list,
        'page_obj': page_obj,
        'total': total,
        'ativos': ativos,
        'concluidos': concluidos,
        'canceladas': canceladas,
        'filtro_sala': sala_id or '',
        'filtro_data': data_str or '',
        'now': agora,
        'is_admin': is_admin,
    }
    return render(request, 'reservas/admin_reservas.html', context)


@csrf_exempt
@staff_member_required(login_url='/login/')
def api_admin_cancel_reserva(request, reserva_id):
    """API para administradores cancelarem qualquer reserva."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido.'}, status=405)

    # Apenas superusuários podem cancelar reservas
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Apenas administradores podem cancelar reservas.'}, status=403)

    try:
        reserva = Reserva.objects.get(id=reserva_id)
    except Reserva.DoesNotExist:
        return JsonResponse({'error': 'Reserva não encontrada.'}, status=404)

    if reserva.cancelada:
        return JsonResponse({'error': 'Esta reserva já foi cancelada.'}, status=400)

    agora = timezone.now()
    if reserva.fim < agora:
        return JsonResponse({'error': 'Não é possível cancelar uma reserva já concluída.'}, status=400)

    reserva.cancelada = True
    reserva.save()
    logger.info(f"Reserva cancelada (admin): {reserva_id} - Admin {request.user.username}")
    return JsonResponse({'success': True, 'message': 'Reserva cancelada com sucesso.'}, status=200)


@csrf_exempt
def api_horarios_disponiveis(request, sala_id):
    """
    API GET para buscar horários disponíveis de uma sala em uma data específica.
    Query params: ?data=YYYY-MM-DD
    """
    if request.method != "GET":
        return JsonResponse({"detail": "Método não permitido."}, status=405)
    
    try:
        sala = Sala.objects.get(id=sala_id)
    except Sala.DoesNotExist:
        return JsonResponse({"detail": "Sala não encontrada."}, status=404)
    
    data_str = request.GET.get('data')
    if not data_str:
        return JsonResponse({"detail": "Parâmetro 'data' é obrigatório (formato: YYYY-MM-DD)."}, status=400)
    
    try:
        from datetime import datetime
        data_selecionada = datetime.strptime(data_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({"detail": "Formato de data inválido. Use YYYY-MM-DD."}, status=400)
    
    # Define os horários padrão (2 horas cada)
    horarios_padrao = [
        ("08:00", "10:00"),
        ("10:00", "12:00"),
        ("12:00", "14:00"),
        ("14:00", "16:00"),
        ("16:00", "18:00"),
        ("18:00", "20:00"),
        ("20:00", "22:00"),
    ]
    
    # Busca reservas existentes para essa sala nessa data (não canceladas)
    from datetime import datetime as dt, time as dt_time
    from django.utils import timezone
    
    reservas_dia = Reserva.objects.filter(
        sala=sala,
        inicio__date=data_selecionada,
        cancelada=False
    )
    
    agora = timezone.now()
    
    horarios_disponiveis = []
    for inicio_str, fim_str in horarios_padrao:
        # Cria datetime timezone-aware para verificar conflitos
        inicio_time = dt.strptime(inicio_str, '%H:%M').time()
        fim_time = dt.strptime(fim_str, '%H:%M').time()
        
        inicio_dt = timezone.make_aware(dt.combine(data_selecionada, inicio_time))
        fim_dt = timezone.make_aware(dt.combine(data_selecionada, fim_time))
        
        # Verifica se o horário já passou
        horario_passado = inicio_dt < agora
        
        # Verifica se há conflito com alguma reserva existente
        conflito = reservas_dia.filter(
            inicio__lt=fim_dt,
            fim__gt=inicio_dt
        ).exists()
        
        horarios_disponiveis.append({
            "inicio": inicio_str,
            "fim": fim_str,
            "range": f"{inicio_str} - {fim_str}",
            "disponivel": not conflito and not horario_passado
        })
    
    return JsonResponse(horarios_disponiveis, safe=False, status=200)


@login_required(login_url="/login/")
@csrf_exempt
def api_criar_reserva(request):
    """
    API POST para criar uma nova reserva.
    Body JSON: {"sala_id": 1, "data": "YYYY-MM-DD", "inicio": "HH:MM", "fim": "HH:MM"}
    """
    if request.method != "POST":
        return JsonResponse({"detail": "Método não permitido."}, status=405)
    
    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"detail": "JSON inválido."}, status=400)
    
    # Validações
    required = ["sala_id", "data", "inicio", "fim"]
    missing = [f for f in required if f not in data]
    if missing:
        return JsonResponse({"detail": f"Campos obrigatórios faltando: {', '.join(missing)}"}, status=400)
    
    try:
        sala = Sala.objects.get(id=data["sala_id"])
    except Sala.DoesNotExist:
        return JsonResponse({"detail": "Sala não encontrada."}, status=404)
    
    # Verifica se a sala está ativa (não deletada por soft delete)
    if not sala.ativo:
        return JsonResponse({"detail": "Esta sala não está mais disponível para reservas."}, status=400)
    
    try:
        from datetime import datetime as dt
        data_reserva = dt.strptime(data["data"], '%Y-%m-%d').date()
        hora_inicio = dt.strptime(data["inicio"], '%H:%M').time()
        hora_fim = dt.strptime(data["fim"], '%H:%M').time()
        
        inicio_dt = dt.combine(data_reserva, hora_inicio)
        fim_dt = dt.combine(data_reserva, hora_fim)
        
        # Adiciona timezone
        from django.utils import timezone as tz
        inicio_dt = tz.make_aware(inicio_dt)
        fim_dt = tz.make_aware(fim_dt)
        
    except ValueError as e:
        return JsonResponse({"detail": f"Formato de data/hora inválido: {str(e)}"}, status=400)
    
    # Validação: Não permitir reservas em datas/horários passados
    agora = timezone.now()
    if inicio_dt < agora:
        return JsonResponse({
            "detail": "Não é possível fazer reservas para datas ou horários que já passaram."
        }, status=400)
    
    # Verifica se o usuário já tem outra reserva neste horário (não cancelada)
    reserva_usuario = Reserva.objects.filter(
        usuario=request.user.username,
        inicio__lt=fim_dt,
        fim__gt=inicio_dt,
        cancelada=False
    ).first()
    
    if reserva_usuario:
        return JsonResponse({
            "detail": f"Você já tem uma reserva para este horário na sala {reserva_usuario.sala.nome}."
        }, status=400)
    
    # Verifica se já não há conflito na sala (apenas reservas não canceladas)
    conflito = Reserva.objects.filter(
        sala=sala,
        inicio__lt=fim_dt,
        fim__gt=inicio_dt,
        cancelada=False
    ).exists()
    
    if conflito:
        return JsonResponse({"detail": "Este horário já está reservado para esta sala."}, status=400)
    
    # Cria a reserva
    reserva = Reserva.objects.create(
        sala=sala,
        usuario=request.user.username,
        inicio=inicio_dt,
        fim=fim_dt
    )
    
    logger.info(f"Reserva criada: {reserva.id} - Sala {sala.nome} - Usuário {request.user.username}")
    
    return JsonResponse({
        "id": reserva.id,
        "sala": {
            "id": sala.id,
            "nome": sala.nome,
            "localizacao": getattr(sala, 'localizacao', '')
        },
        "data": data_reserva.strftime('%d/%m/%Y'),
        "horario": f"{data['inicio']} - {data['fim']}",
        "inicio": reserva.inicio.isoformat(),
        "fim": reserva.fim.isoformat(),
    }, status=201)


@login_required(login_url="/login/")
@csrf_exempt
def api_cancelar_reserva(request, reserva_id):
    """
    API POST para cancelar uma reserva.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido."}, status=405)
    
    try:
        reserva = Reserva.objects.get(id=reserva_id, usuario=request.user.username)
    except Reserva.DoesNotExist:
        return JsonResponse({"error": "Reserva não encontrada."}, status=404)
    
    # Verifica se a reserva já foi cancelada
    if reserva.cancelada:
        return JsonResponse({"error": "Esta reserva já foi cancelada."}, status=400)
    
    # Verifica se a reserva já passou
    agora = timezone.now()
    if reserva.fim < agora:
        return JsonResponse({"error": "Não é possível cancelar uma reserva já concluída."}, status=400)
    
    # Marca a reserva como cancelada
    reserva.cancelada = True
    reserva.save()
    logger.info(f"Reserva cancelada: {reserva_id} - Usuário {request.user.username}")
    
    return JsonResponse({"success": True, "message": "Reserva cancelada com sucesso."}, status=200)


# ============================================
#  GERENCIAR USUÁRIOS (ADMIN)
# ============================================

def get_user_type(user):
    """Determina o tipo do usuário baseado em seus atributos."""
    if user.is_superuser or user.is_staff:
        return 'admin'
    # Verifica se o username parece ser matrícula de professor (SIAPE)
    if user.username.upper().startswith('SIAPE') or (hasattr(user, 'first_name') and 'Prof' in (user.first_name or '')):
        return 'professor'
    return 'estudante'


@staff_member_required(login_url='/login/')
def gerenciar_usuarios(request):
    """Renderiza a interface administrativa de gerenciamento de usuários."""
    
    # Filtros via query params
    tipo_filter = request.GET.get('tipo', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('q', '')
    
    # Busca todos os usuários (exceto o próprio admin logado para evitar auto-desativação acidental)
    usuarios_qs = User.objects.all().order_by('first_name', 'last_name', 'username')
    
    # Aplica filtro de busca
    if search_query:
        usuarios_qs = usuarios_qs.filter(
            models.Q(first_name__icontains=search_query) |
            models.Q(last_name__icontains=search_query) |
            models.Q(email__icontains=search_query) |
            models.Q(username__icontains=search_query)
        )
    
    # Aplica filtro de status
    if status_filter == 'ativo':
        usuarios_qs = usuarios_qs.filter(is_active=True)
    elif status_filter == 'inativo':
        usuarios_qs = usuarios_qs.filter(is_active=False)
    
    # Estatísticas
    all_users = User.objects.all()
    total_usuarios = all_users.count()
    usuarios_ativos = all_users.filter(is_active=True).count()
    
    # Conta por tipo (exclui admins da contagem de estudantes/professores)
    total_estudantes = 0
    total_professores = 0
    
    for u in all_users.filter(is_staff=False, is_superuser=False):
        if get_user_type(u) == 'professor':
            total_professores += 1
        else:
            total_estudantes += 1
    
    # Prepara dados dos usuários
    usuarios_data = []
    for u in usuarios_qs:
        tipo = get_user_type(u)
        
        # Aplica filtro de tipo
        if tipo_filter and tipo != tipo_filter:
            continue
        
        # Conta reservas do usuário
        reservas_count = Reserva.objects.filter(usuario=u.username).count()
        
        # Nome completo ou username
        nome = f"{u.first_name} {u.last_name}".strip() or u.username
        
        # Matrícula (username) ou SIAPE
        matricula = u.username
        
        usuarios_data.append({
            'id': u.id,
            'nome': nome,
            'email': u.email,
            'matricula': matricula,
            'tipo': tipo,
            'tipo_display': {'estudante': 'Estudante', 'professor': 'Professor', 'admin': 'Administrador'}.get(tipo, tipo.title()),
            'status': 'ativo' if u.is_active else 'inativo',
            'status_display': 'Ativo' if u.is_active else 'Inativo',
            'is_active': u.is_active,
            'reservas_count': reservas_count,
        })
    
    # Paginação
    paginator = Paginator(usuarios_data, 8)  # 8 usuários por página
    page_number = request.GET.get('page', 1)
    try:
        page_obj = paginator.get_page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page_obj = paginator.get_page(1)
    
    # Apenas superusuários podem ativar/desativar usuários
    is_admin = request.user.is_superuser
    
    context = {
        'usuarios': page_obj.object_list,
        'page_obj': page_obj,
        'total_usuarios': total_usuarios,
        'usuarios_ativos': usuarios_ativos,
        'total_estudantes': total_estudantes,
        'total_professores': total_professores,
        'filtro_tipo': tipo_filter,
        'filtro_status': status_filter,
        'search_query': search_query,
        'is_admin': is_admin,
    }
    
    return render(request, 'reservas/gerenciar_usuarios.html', context)


@staff_member_required(login_url='/login/')
@csrf_exempt
def api_toggle_usuario(request, usuario_id):
    """API para ativar/desativar um usuário."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido.'}, status=405)
    
    # Apenas superusuários podem alterar status de usuários
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Apenas administradores podem alterar status de usuários.'}, status=403)
    
    try:
        usuario = User.objects.get(id=usuario_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuário não encontrado.'}, status=404)
    
    # Impede que o admin desative a si mesmo
    if usuario.id == request.user.id:
        return JsonResponse({'error': 'Você não pode desativar sua própria conta.'}, status=400)
    
    # Impede desativação de superusuários por usuários staff comuns
    if usuario.is_superuser and not request.user.is_superuser:
        return JsonResponse({'error': 'Apenas superusuários podem desativar outros superusuários.'}, status=403)
    
    # Toggle do status
    usuario.is_active = not usuario.is_active
    usuario.save()
    
    action = 'ativado' if usuario.is_active else 'desativado'
    logger.info(f"Usuário {action}: {usuario.username} por {request.user.username}")
    
    return JsonResponse({
        'success': True,
        'message': f'Usuário {action} com sucesso!',
        'is_active': usuario.is_active,
    })


# ============================================
#  DASHBOARD ADMINISTRATIVO
# ============================================

@staff_member_required(login_url='/login/')
def admin_dashboard(request):
    """Renderiza o dashboard administrativo com estatísticas e gráficos."""
    agora = timezone.now()
    
    # === KPIs ===
    # Total de reservas
    total_reservas = Reserva.objects.count()
    
    # Reservas do mês atual vs mês anterior
    inicio_mes_atual = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    inicio_mes_anterior = (inicio_mes_atual - timedelta(days=1)).replace(day=1)
    
    reservas_mes_atual = Reserva.objects.filter(inicio__gte=inicio_mes_atual).count()
    reservas_mes_anterior = Reserva.objects.filter(
        inicio__gte=inicio_mes_anterior,
        inicio__lt=inicio_mes_atual
    ).count()
    
    # Calcular variação percentual
    if reservas_mes_anterior > 0:
        variacao_reservas = round(((reservas_mes_atual - reservas_mes_anterior) / reservas_mes_anterior) * 100)
    else:
        variacao_reservas = 100 if reservas_mes_atual > 0 else 0
    
    # Salas
    total_salas = Sala.objects.filter(ativo=True).count()
    salas_disponiveis = Sala.objects.filter(ativo=True, status='Disponivel').count()
    salas_manutencao = Sala.objects.filter(ativo=True, status='Em Manutenção').count()
    
    # Usuários
    total_usuarios = User.objects.filter(is_active=True).count()
    total_estudantes = User.objects.filter(is_active=True, is_staff=False, is_superuser=False).count()
    total_professores = User.objects.filter(is_active=True, is_staff=True, is_superuser=False).count()
    
    # Taxa de ocupação (reservas ativas / capacidade total)
    # Simplificação: porcentagem de horários ocupados nas últimas 4 semanas
    inicio_periodo = agora - timedelta(days=28)
    reservas_periodo = Reserva.objects.filter(
        inicio__gte=inicio_periodo,
        cancelada=False
    ).count()
    # Assumindo 10 horários por dia por sala, 5 dias por semana, 4 semanas
    capacidade_teorica = total_salas * 10 * 5 * 4 if total_salas > 0 else 1
    taxa_ocupacao = min(round((reservas_periodo / capacidade_teorica) * 100), 100)
    
    # === Dados para gráficos ===
    # Reservas por mês (últimos 6 meses)
    seis_meses_atras = agora - timedelta(days=180)
    reservas_por_mes = (
        Reserva.objects.filter(inicio__gte=seis_meses_atras)
        .annotate(mes=TruncMonth('inicio'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )
    
    meses_br = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    dados_mensais = []
    for item in reservas_por_mes:
        if item['mes']:
            dados_mensais.append({
                'month': meses_br[item['mes'].month - 1],
                'total': item['total']
            })
    
    # Se não houver dados, mostrar lista vazia (dados reais)
    if not dados_mensais:
        dados_mensais = []
    
    # Taxa de uso por sala (top 5 salas mais usadas)
    uso_por_sala = (
        Reserva.objects.filter(cancelada=False)
        .values('sala__nome')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )
    
    dados_salas = []
    max_reservas = max([s['total'] for s in uso_por_sala]) if uso_por_sala else 1
    for item in uso_por_sala:
        # Converter para porcentagem relativa
        uso_pct = round((item['total'] / max_reservas) * 100) if max_reservas > 0 else 0
        dados_salas.append({
            'name': item['sala__nome'],
            'usage': uso_pct
        })
    
    # Dados reais - não usar fallback mockado
    
    # === Alertas ===
    # Reservas sem comparecimento (reservas passadas não canceladas - simplificado)
    reservas_hoje = Reserva.objects.filter(
        inicio__date=agora.date(),
        fim__lt=agora,
        cancelada=False
    ).count()
    
    # === Próximas Reservas ===
    proximas_reservas = (
        Reserva.objects.filter(
            inicio__gte=agora,
            cancelada=False
        )
        .select_related('sala')
        .order_by('inicio')[:5]
    )
    
    proximas_lista = []
    for r in proximas_reservas:
        usuario_obj = User.objects.filter(username=r.usuario).first()
        nome = usuario_obj.get_full_name() if usuario_obj and usuario_obj.first_name else r.usuario
        proximas_lista.append({
            'sala': r.sala.nome,
            'horario': r.inicio.strftime('%H:%M'),
            'usuario': nome,
        })
    
    # Dados reais - lista vazia se não houver reservas
    
    # Verificar se é admin
    is_admin = request.user.is_superuser
    
    context = {
        # KPIs
        'total_reservas': total_reservas,
        'variacao_reservas': variacao_reservas,
        'total_salas': total_salas,
        'salas_disponiveis': salas_disponiveis,
        'salas_manutencao': salas_manutencao,
        'total_usuarios': total_usuarios,
        'total_estudantes': total_estudantes,
        'total_professores': total_professores,
        'taxa_ocupacao': taxa_ocupacao,
        
        # Gráficos (JSON para JavaScript)
        'dados_mensais_json': json.dumps(dados_mensais),
        'dados_salas_json': json.dumps(dados_salas),
        
        # Alertas
        'salas_manutencao_count': salas_manutencao,
        'reservas_sem_comparecimento': reservas_hoje,
        
        # Próximas reservas
        'proximas_reservas': proximas_lista,
        
        # Permissões
        'is_admin': is_admin,
    }
    
    return render(request, 'reservas/admin_dashboard.html', context)


@staff_member_required(login_url='/login/')
def api_dashboard_data(request):
    """API para retornar dados atualizados do dashboard (para refresh)."""
    # Esta API pode ser usada para atualização dinâmica via AJAX
    agora = timezone.now()
    
    total_reservas = Reserva.objects.count()
    total_salas = Sala.objects.filter(ativo=True).count()
    total_usuarios = User.objects.filter(is_active=True).count()
    
    return JsonResponse({
        'total_reservas': total_reservas,
        'total_salas': total_salas,
        'total_usuarios': total_usuarios,
    })
