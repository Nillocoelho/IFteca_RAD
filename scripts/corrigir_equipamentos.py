"""
Script para corrigir equipamentos das salas existentes.
Converte strings como "Projetor, Ar-condicionado" para listas ["Projetor", "Ar condicionado"]
"""
import os
import sys
import django

# Configura o Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ifteca_project.settings')
django.setup()

from salas.models import Sala


def corrigir_equipamentos():
    """Corrige equipamentos que estão como string para lista."""
    print('\n=== CORRIGINDO EQUIPAMENTOS DAS SALAS ===\n')
    
    salas = Sala.objects.all()
    corrigidas = 0
    
    for sala in salas:
        # Se equipamentos é uma string, converte para lista
        if isinstance(sala.equipamentos, str):
            if sala.equipamentos.strip():
                # Divide por vírgula e limpa espaços
                equipamentos_lista = [
                    equip.strip() for equip in sala.equipamentos.split(',')
                    if equip.strip()
                ]
                sala.equipamentos = equipamentos_lista
                sala.save()
                print(f'✓ Corrigida: {sala.nome}')
                print(f'  Antes: "{sala.equipamentos}"')
                print(f'  Depois: {equipamentos_lista}')
                corrigidas += 1
            else:
                # String vazia, converte para lista vazia
                sala.equipamentos = []
                sala.save()
                print(f'✓ Corrigida (vazia): {sala.nome}')
                corrigidas += 1
        elif isinstance(sala.equipamentos, list):
            print(f'• OK: {sala.nome} (já é lista)')
        else:
            print(f'⚠ Ignorada: {sala.nome} (tipo desconhecido: {type(sala.equipamentos)})')
    
    print(f'\n📊 Total de salas verificadas: {salas.count()}')
    print(f'✨ Salas corrigidas: {corrigidas}')


if __name__ == '__main__':
    corrigir_equipamentos()
