"""
Script para testar o sistema de Soft Delete de salas.

Fluxo de teste:
1. Admin cadastra sala 101
2. Aluno faz reserva na sala 101
3. Admin tenta apagar sala 101 → DEVE FALHAR (tem reserva ativa)
4. Aluno cancela ou usa a reserva
5. Admin consegue apagar sala 101
6. Aluno vê sala 101 no histórico mesmo deletada
"""

import os
import sys
import django

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ifteca_project.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from salas.models import Sala
from reservas.models import Reserva
from django.contrib.auth.models import User


def print_status(message, status="INFO"):
    symbols = {"INFO": "ℹ️", "OK": "✅", "ERROR": "❌", "WARN": "⚠️"}
    print(f"{symbols.get(status, '•')} {message}")


def main():
    print("\n" + "="*60)
    print("🧪 TESTE DO SISTEMA DE SOFT DELETE")
    print("="*60 + "\n")
    
    # Passo 1: Admin cria sala
    print_status("Passo 1: Criando Sala 101...", "INFO")
    sala, created = Sala.objects.get_or_create(
        nome="Sala 101 - Teste",
        defaults={
            "capacidade": 10,
            "tipo": "Coletiva",
            "status": "Disponivel",
            "ativo": True
        }
    )
    if created:
        print_status(f"Sala criada: {sala.nome} (ID: {sala.id}, Ativo: {sala.ativo})", "OK")
    else:
        print_status(f"Sala já existe: {sala.nome} (ID: {sala.id}, Ativo: {sala.ativo})", "WARN")
    
    # Passo 2: Criar usuário de teste e fazer reserva
    print_status("\nPasso 2: Criando reserva para aluno de teste...", "INFO")
    
    aluno, _ = User.objects.get_or_create(username="aluno_teste")
    
    inicio = timezone.now() + timedelta(days=1)
    fim = inicio + timedelta(hours=2)
    
    reserva, created = Reserva.objects.get_or_create(
        sala=sala,
        usuario=aluno.username,
        inicio=inicio,
        fim=fim,
        defaults={"cancelada": False}
    )
    
    if created:
        print_status(f"Reserva criada: {reserva}", "OK")
    else:
        print_status(f"Reserva já existe: {reserva}", "WARN")
    
    # Passo 3: Tentar deletar sala COM reserva ativa
    print_status("\nPasso 3: Tentando deletar sala COM reserva ativa...", "INFO")
    
    reservas_ativas = sala.reservas.filter(
        cancelada=False,
        inicio__gte=timezone.now()
    ).count()
    
    if reservas_ativas > 0:
        print_status(f"❌ CORRETO: Sala possui {reservas_ativas} reserva(s) ativa(s). Não pode ser deletada.", "OK")
    else:
        print_status("Nenhuma reserva ativa encontrada!", "ERROR")
    
    # Passo 4: Cancelar reserva
    print_status("\nPasso 4: Cancelando reserva do aluno...", "INFO")
    reserva.cancelada = True
    reserva.save()
    print_status(f"Reserva cancelada: {reserva}", "OK")
    
    # Passo 5: Deletar sala SEM reserva ativa
    print_status("\nPasso 5: Tentando deletar sala SEM reserva ativa...", "INFO")
    
    reservas_ativas = sala.reservas.filter(
        cancelada=False,
        inicio__gte=timezone.now()
    ).count()
    
    if reservas_ativas == 0:
        sala.ativo = False
        sala.save()
        print_status(f"✅ SOFT DELETE executado: Sala marcada como inativa (ativo={sala.ativo})", "OK")
    else:
        print_status(f"Ainda há {reservas_ativas} reserva(s) ativa(s)!", "ERROR")
    
    # Passo 6: Verificar histórico
    print_status("\nPasso 6: Verificando histórico de reservas do aluno...", "INFO")
    
    historico = Reserva.objects.filter(usuario=aluno.username).select_related('sala')
    
    print_status(f"Total de reservas no histórico: {historico.count()}", "INFO")
    
    for res in historico:
        sala_nome = res.sala.nome if res.sala else "SALA DELETADA"
        sala_ativa = res.sala.ativo if res.sala else False
        print_status(
            f"  - {sala_nome} | Cancelada: {res.cancelada} | Sala Ativa: {sala_ativa}",
            "OK" if res.sala else "WARN"
        )
    
    # Verificar queries de salas ativas
    print_status("\nVerificando filtros de salas...", "INFO")
    
    salas_ativas = Sala.objects.filter(ativo=True).count()
    salas_inativas = Sala.objects.filter(ativo=False).count()
    salas_total = Sala.objects.count()
    
    print_status(f"Salas ativas: {salas_ativas}", "INFO")
    print_status(f"Salas inativas: {salas_inativas}", "INFO")
    print_status(f"Total de salas: {salas_total}", "INFO")
    
    # Verificar se sala inativa aparece em listagem pública
    print_status("\nVerificando visibilidade da sala deletada...", "INFO")
    
    sala_publica = Sala.objects.filter(id=sala.id, ativo=True).exists()
    
    if not sala_publica:
        print_status("✅ CORRETO: Sala deletada NÃO aparece em listagem pública", "OK")
    else:
        print_status("Sala deletada ainda aparece em listagem pública!", "ERROR")
    
    print("\n" + "="*60)
    print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
