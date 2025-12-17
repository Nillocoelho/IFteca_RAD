"""
Script para criar salas de exemplo.
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


def criar_salas_exemplo():
    """Cria salas de exemplo para teste."""
    print('\n=== CRIANDO SALAS DE EXEMPLO ===\n')
    
    salas_data = [
        {
            'nome': 'Sala 101',
            'capacidade': 20,
            'tipo': 'Grupo',
            'localizacao': '1º Andar - Bloco A',
            'descricao': 'Sala confortável para estudos em grupo maior.',
            'equipamentos': ['Quadro branco', 'Ar condicionado', 'Projetor'],
            'status': 'Disponivel'
        },
        {
            'nome': 'Sala 102',
            'capacidade': 15,
            'tipo': 'Grupo',
            'localizacao': '1º Andar - Bloco A',
            'descricao': 'Sala confortável para estudos em grupo menor.',
            'equipamentos': ['Quadro branco', 'Ar condicionado'],
            'status': 'Disponivel'
        },
        {
            'nome': 'Sala 201',
            'capacidade': 25,
            'tipo': 'Grupo',
            'localizacao': '2º Andar - Bloco A',
            'descricao': 'Sala ampla para apresentações e estudos em grupo.',
            'equipamentos': ['Quadro branco', 'Ar condicionado', 'Projetor', 'TV'],
            'status': 'Disponivel'
        },
    ]
    
    criadas = 0
    for sala_info in salas_data:
        sala, created = Sala.objects.get_or_create(
            nome=sala_info['nome'],
            defaults=sala_info
        )
        
        if created:
            print(f'✓ Sala criada: {sala.nome} - Capacidade: {sala.capacidade}')
            criadas += 1
        else:
            print(f'• Sala já existe: {sala.nome}')
    
    print(f'\n📊 Total de salas: {Sala.objects.count()}')
    print(f'✨ Salas criadas agora: {criadas}')


if __name__ == '__main__':
    criar_salas_exemplo()
