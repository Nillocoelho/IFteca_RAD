# -*- coding: utf-8 -*-
"""
Script para popular o banco de dados com dados fictícios usando Faker.
Cria salas, usuários e reservas para teste do dashboard.

Executar com: python manage.py shell < scripts/popular_banco_faker.py
Ou: docker exec -i ifteca_rad-web-1 python manage.py shell < scripts/popular_banco_faker.py
"""

import random
from datetime import datetime, timedelta
from faker import Faker
from django.contrib.auth.models import User
from django.utils import timezone
from salas.models import Sala
from reservas.models import Reserva

fake = Faker('pt_BR')

print("=" * 60)
print("POPULANDO BANCO DE DADOS COM FAKER")
print("=" * 60)

# ============================================
# CONFIGURACOES
# ============================================
NUM_SALAS = 15
NUM_ESTUDANTES = 30
NUM_PROFESSORES = 8
NUM_RESERVAS = 200

# ============================================
# CRIAR SALAS
# ============================================
print("\nCriando Salas...")

# Usar strings ASCII para evitar problemas de encoding
tipos_sala = ['Coletiva', 'Auditorio']
status_sala = ['Disponivel', 'Disponivel', 'Disponivel', 'Em Manutencao']  # Mais disponiveis
localizacoes = ['Bloco A', 'Bloco B', 'Bloco C', 'Biblioteca', 'Terreo', 'Anexo']
equipamentos_opcoes = [
    ['Projetor', 'Ar condicionado'],
    ['Computadores', 'Ar condicionado'],
    ['Quadro branco', 'Projetor'],
    ['TV', 'Ar condicionado', 'Webcam'],
    ['Lousa digital', 'Projetor'],
    ['Computadores', 'Projetor', 'Ar condicionado'],
]

salas_criadas = 0
for i in range(NUM_SALAS):
    numero = f"{random.choice([1, 2, 3])}{str(i+1).zfill(2)}"
    nome = f"Sala {numero}"
    
    # Evitar duplicatas
    if Sala.objects.filter(nome=nome).exists():
        continue
    
    sala = Sala.objects.create(
        nome=nome,
        tipo=random.choice(tipos_sala),
        capacidade=random.choice([4, 6, 8, 10, 12, 15, 20]),
        status=random.choice(status_sala),
        localizacao=random.choice(localizacoes),
        equipamentos=random.choice(equipamentos_opcoes),
        descricao=fake.sentence(nb_words=10),
        ativo=True
    )
    salas_criadas += 1
    print(f"  ✓ {sala.nome} ({sala.tipo})")

print(f"\n  Total de salas criadas: {salas_criadas}")

# ============================================
# CRIAR ESTUDANTES
# ============================================
print("\n👨‍🎓 Criando Estudantes...")

estudantes_criados = 0
for i in range(NUM_ESTUDANTES):
    primeiro_nome = fake.first_name()
    sobrenome = fake.last_name()
    username = f"estudante{i+1:03d}"
    
    if User.objects.filter(username=username).exists():
        continue
    
    user = User.objects.create_user(
        username=username,
        email=f"{username}@estudante.ifpb.edu.br",
        password="senha123",
        first_name=primeiro_nome,
        last_name=sobrenome,
        is_staff=False,
        is_superuser=False,
        is_active=True
    )
    estudantes_criados += 1
    print(f"  ✓ {user.get_full_name()} ({user.username})")

print(f"\n  Total de estudantes criados: {estudantes_criados}")

# ============================================
# CRIAR PROFESSORES
# ============================================
print("\n👨‍🏫 Criando Professores...")

professores_criados = 0
for i in range(NUM_PROFESSORES):
    primeiro_nome = fake.first_name()
    sobrenome = fake.last_name()
    username = f"professor{i+1:03d}"
    
    if User.objects.filter(username=username).exists():
        continue
    
    user = User.objects.create_user(
        username=username,
        email=f"{username}@ifpb.edu.br",
        password="senha123",
        first_name=primeiro_nome,
        last_name=sobrenome,
        is_staff=False,      # Professor não é staff/admin
        is_superuser=False,
        is_active=True
    )
    professores_criados += 1
    print(f"  ✓ Prof. {user.get_full_name()} ({user.username})")

print(f"\n  Total de professores criados: {professores_criados}")

# ============================================
# CRIAR RESERVAS
# ============================================
print("\n📅 Criando Reservas...")

# Buscar todas as salas e usuários (somente não-staff)
salas = list(Sala.objects.filter(ativo=True))
usuarios = list(User.objects.filter(is_active=True, is_staff=False, is_superuser=False))

if not salas:
    print("  ❌ Nenhuma sala encontrada!")
elif not usuarios:
    print("  ❌ Nenhum usuário encontrado!")
else:
    reservas_criadas = 0
    reservas_canceladas = 0
    
    # Distribuir reservas nos últimos 6 meses e próximas 2 semanas
    agora = timezone.now()
    inicio_periodo = agora - timedelta(days=180)  # 6 meses atrás
    fim_periodo = agora + timedelta(days=14)  # 2 semanas no futuro
    
    # Horários possíveis (8h às 21h)
    horarios = [8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20]
    
    for i in range(NUM_RESERVAS):
        # Data aleatória no período
        dias_offset = random.randint(0, (fim_periodo - inicio_periodo).days)
        data_reserva = inicio_periodo + timedelta(days=dias_offset)
        
        # Pular fins de semana
        if data_reserva.weekday() >= 5:
            continue
        
        # Horário aleatório
        hora_inicio = random.choice(horarios)
        hora_fim = hora_inicio + random.choice([1, 2])  # 1 ou 2 horas
        
        inicio = data_reserva.replace(hour=hora_inicio, minute=0, second=0, microsecond=0)
        fim = data_reserva.replace(hour=hora_fim, minute=0, second=0, microsecond=0)
        
        # Sala e usuário aleatórios
        sala = random.choice(salas)
        usuario = random.choice(usuarios)  # garantidamente não-staff
        
        # Verificar se já existe reserva no mesmo horário/sala
        conflito = Reserva.objects.filter(
            sala=sala,
            inicio__lt=fim,
            fim__gt=inicio,
            cancelada=False
        ).exists()
        
        if conflito:
            continue
        
        # 10% das reservas são canceladas
        cancelada = random.random() < 0.1
        
        reserva = Reserva.objects.create(
            sala=sala,
            usuario=usuario.username,
            inicio=inicio,
            fim=fim,
            cancelada=cancelada
        )
        
        reservas_criadas += 1
        if cancelada:
            reservas_canceladas += 1
        
        if reservas_criadas % 20 == 0:
            print(f"  ... {reservas_criadas} reservas criadas")
    
    print(f"\n  Total de reservas criadas: {reservas_criadas}")
    print(f"  Reservas canceladas: {reservas_canceladas}")
    print(f"  Reservas ativas: {reservas_criadas - reservas_canceladas}")

# ============================================
# RESUMO FINAL
# ============================================
print("\n" + "=" * 60)
print("📊 RESUMO DO BANCO DE DADOS")
print("=" * 60)
print(f"  Salas Ativas: {Sala.objects.filter(ativo=True).count()}")
print(f"  Salas Disponíveis: {Sala.objects.filter(ativo=True, status='Disponivel').count()}")
print(f"  Salas em Manutenção: {Sala.objects.filter(ativo=True, status='Em Manutenção').count()}")
print(f"  Usuários Ativos: {User.objects.filter(is_active=True).count()}")
print(f"  Estudantes: {User.objects.filter(is_active=True, is_staff=False, is_superuser=False).count()}")
print(f"  Professores: {User.objects.filter(is_active=True, username__startswith='professor').count()}")
print(f"  Total de Reservas: {Reserva.objects.count()}")
print(f"  Reservas Ativas: {Reserva.objects.filter(cancelada=False).count()}")
print(f"  Reservas Canceladas: {Reserva.objects.filter(cancelada=True).count()}")
print("=" * 60)
print("✅ BANCO POPULADO COM SUCESSO!")
print("=" * 60)
