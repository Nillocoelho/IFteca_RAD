"""
Script para criar reservas de exemplo para teste.
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Configura o Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ifteca_project.settings')
django.setup()

from django.utils import timezone
from reservas.models import Reserva
from salas.models import Sala
from django.contrib.auth.models import User


def criar_reservas_exemplo():
    """Cria reservas de exemplo para teste."""
    print('\n=== CRIANDO RESERVAS DE EXEMPLO ===\n')
    
    # Busca uma sala
    try:
        sala = Sala.objects.first()
        if not sala:
            print('❌ Nenhuma sala encontrada. Crie salas primeiro.')
            return
    except Exception as e:
        print(f'❌ Erro ao buscar sala: {e}')
        return
    
    # Busca um usuário estudante
    try:
        usuario = User.objects.filter(is_staff=False, is_superuser=False).first()
        if not usuario:
            print('❌ Nenhum estudante encontrado. Crie estudantes primeiro.')
            return
    except Exception as e:
        print(f'❌ Erro ao buscar usuário: {e}')
        return
    
    # Data base: amanhã
    base_date = datetime.now().date() + timedelta(days=1)
    
    reservas_criadas = []
    
    # Reserva 1: Amanhã 14:00-16:00
    inicio1 = timezone.make_aware(datetime.combine(base_date, datetime.strptime('14:00', '%H:%M').time()))
    fim1 = timezone.make_aware(datetime.combine(base_date, datetime.strptime('16:00', '%H:%M').time()))
    
    reserva1, created1 = Reserva.objects.get_or_create(
        sala=sala,
        usuario=usuario.username,
        inicio=inicio1,
        fim=fim1
    )
    
    if created1:
        reservas_criadas.append(f'✓ Reserva criada: {sala.nome} - {base_date.strftime("%d/%m/%Y")} 14:00-16:00')
    else:
        print(f'• Reserva já existe: {sala.nome} - {base_date.strftime("%d/%m/%Y")} 14:00-16:00')
    
    # Reserva 2: Depois de amanhã 10:00-12:00
    base_date2 = base_date + timedelta(days=1)
    inicio2 = timezone.make_aware(datetime.combine(base_date2, datetime.strptime('10:00', '%H:%M').time()))
    fim2 = timezone.make_aware(datetime.combine(base_date2, datetime.strptime('12:00', '%H:%M').time()))
    
    reserva2, created2 = Reserva.objects.get_or_create(
        sala=sala,
        usuario=usuario.username,
        inicio=inicio2,
        fim=fim2
    )
    
    if created2:
        reservas_criadas.append(f'✓ Reserva criada: {sala.nome} - {base_date2.strftime("%d/%m/%Y")} 10:00-12:00')
    else:
        print(f'• Reserva já existe: {sala.nome} - {base_date2.strftime("%d/%m/%Y")} 10:00-12:00')
    
    # Reserva 3: Passada (para histórico)
    past_date = datetime.now().date() - timedelta(days=2)
    inicio3 = timezone.make_aware(datetime.combine(past_date, datetime.strptime('08:00', '%H:%M').time()))
    fim3 = timezone.make_aware(datetime.combine(past_date, datetime.strptime('10:00', '%H:%M').time()))
    
    reserva3, created3 = Reserva.objects.get_or_create(
        sala=sala,
        usuario=usuario.username,
        inicio=inicio3,
        fim=fim3
    )
    
    if created3:
        reservas_criadas.append(f'✓ Reserva passada criada: {sala.nome} - {past_date.strftime("%d/%m/%Y")} 08:00-10:00')
    else:
        print(f'• Reserva passada já existe: {sala.nome} - {past_date.strftime("%d/%m/%Y")} 08:00-10:00')
    
    print()
    for msg in reservas_criadas:
        print(msg)
    
    print(f'\n📊 Total de reservas do usuário {usuario.username}: {Reserva.objects.filter(usuario=usuario.username).count()}')


if __name__ == '__main__':
    criar_reservas_exemplo()
