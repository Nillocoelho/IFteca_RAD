"""
Script para testar reuso de nomes de salas excluídas.

Fluxo de teste:
1. Criar sala "Sala Teste"
2. Soft delete da sala
3. Tentar criar nova sala com mesmo nome → DEVE FUNCIONAR
"""

import os
import sys
import django

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ifteca_project.settings')
django.setup()

from salas.models import Sala

def main():
    print("\n" + "="*60)
    print("🧪 TESTE: REUSO DE NOMES DE SALAS EXCLUÍDAS")
    print("="*60 + "\n")
    
    # Limpar salas de teste anteriores
    Sala.objects.filter(nome="Sala Teste Duplicado").delete()
    
    # Passo 1: Criar primeira sala
    print("ℹ️  Passo 1: Criando sala 'Sala Teste Duplicado'...")
    sala1 = Sala.objects.create(
        nome="Sala Teste Duplicado",
        capacidade=10,
        tipo="Coletiva",
        ativo=True
    )
    print(f"✅ Sala criada: {sala1.nome} (ID: {sala1.id}, Ativo: {sala1.ativo})")
    
    # Passo 2: Soft delete
    print("\nℹ️  Passo 2: Executando soft delete...")
    sala1.ativo = False
    sala1.save()
    print(f"✅ Soft delete executado: {sala1.nome} (Ativo: {sala1.ativo})")
    
    # Passo 3: Tentar criar sala com mesmo nome
    print("\nℹ️  Passo 3: Tentando criar nova sala com mesmo nome...")
    try:
        sala2 = Sala.objects.create(
            nome="Sala Teste Duplicado",
            capacidade=20,
            tipo="Auditorio",
            ativo=True
        )
        print(f"✅ ✅ SUCESSO: Nova sala criada com mesmo nome!")
        print(f"   Sala 1 (inativa): ID={sala1.id}, Ativo={sala1.ativo}")
        print(f"   Sala 2 (ativa): ID={sala2.id}, Ativo={sala2.ativo}")
    except Exception as e:
        print(f"❌ ERRO: {e}")
        return False
    
    # Verificar estado final
    print("\nℹ️  Verificando estado final...")
    salas = Sala.objects.filter(nome="Sala Teste Duplicado")
    print(f"   Total de salas com nome 'Sala Teste Duplicado': {salas.count()}")
    for s in salas:
        print(f"   - ID: {s.id}, Tipo: {s.tipo}, Ativo: {s.ativo}")
    
    # Tentar criar outra sala ativa com mesmo nome (deve falhar)
    print("\nℹ️  Passo 4: Tentando criar TERCEIRA sala ativa com mesmo nome (deve falhar)...")
    try:
        sala3 = Sala.objects.create(
            nome="Sala Teste Duplicado",
            capacidade=30,
            tipo="Coletiva",
            ativo=True
        )
        print(f"❌ ERRO: Permitiu criar sala duplicada ativa!")
        return False
    except Exception as e:
        print(f"✅ ✅ CORRETO: Impediu criação de sala duplicada ativa")
        print(f"   Erro: {type(e).__name__}")
    
    # Cleanup
    print("\nℹ️  Limpando dados de teste...")
    Sala.objects.filter(nome="Sala Teste Duplicado").delete()
    print("✅ Dados de teste removidos")
    
    print("\n" + "="*60)
    print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
    print("="*60 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
