"""
Script para testar a API de horários disponíveis
"""
import os
import sys
import django
from datetime import date, timedelta

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ifteca_project.settings')
django.setup()

from salas.models import Sala
from reservas.views import api_horarios_disponiveis
from django.http import HttpRequest

def testar_api():
    """Testa a API de horários disponíveis"""
    
    # Pega a primeira sala
    sala = Sala.objects.first()
    if not sala:
        print("❌ Nenhuma sala encontrada no banco")
        return
    
    print(f"✅ Testando sala: {sala.nome} (ID: {sala.id})")
    
    # Cria um request simulado
    request = HttpRequest()
    request.method = 'GET'
    
    # Testa para amanhã
    data_teste = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    request.GET = {'data': data_teste}
    
    print(f"\n🌐 Chamando API com data: {data_teste}")
    
    response = api_horarios_disponiveis(request, sala.id)
    
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        import json
        horarios = json.loads(response.content)
        print(f"✅ API respondeu com {len(horarios)} horários:")
        for h in horarios:
            status = "✅ Disponível" if h['disponivel'] else "❌ Ocupado"
            print(f"  • {h['range']}: {status}")
    else:
        print(f"❌ Erro: {response.content.decode('utf-8')}")

if __name__ == "__main__":
    testar_api()
