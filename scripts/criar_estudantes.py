"""
Script para criar usuários estudantes no sistema IFTECA.
Este script facilita a criação de alunos sem privilégios administrativos.

Uso:
    python scripts/criar_estudantes.py
"""
import os
import sys
import django

# Configura o Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ifteca_project.settings')
django.setup()

from django.contrib.auth.models import User


def criar_estudante(matricula, email, primeiro_nome, sobrenome, senha=None):
    """
    Cria um novo estudante no sistema.
    
    Args:
        matricula: Matrícula do estudante (será o username)
        email: Email do estudante
        primeiro_nome: Primeiro nome
        sobrenome: Sobrenome
        senha: Senha (opcional, padrão: ifpb + matrícula)
    
    Returns:
        User: Objeto do usuário criado ou existente
    """
    if senha is None:
        senha = f'ifpb{matricula}'
    
    user, created = User.objects.get_or_create(
        username=matricula,
        defaults={
            'email': email,
            'first_name': primeiro_nome,
            'last_name': sobrenome,
            'is_staff': False,
            'is_superuser': False,
            'is_active': True
        }
    )
    
    if created:
        user.set_password(senha)
        user.save()
        print(f'✓ Estudante {matricula} criado com sucesso!')
        print(f'  Nome: {primeiro_nome} {sobrenome}')
        print(f'  Email: {email}')
        print(f'  Senha: {senha}')
    else:
        print(f'• Estudante {matricula} já existe no sistema.')
        print(f'  Nome: {user.first_name} {user.last_name}')
        print(f'  Email: {user.email}')
    
    return user


def listar_estudantes():
    """Lista todos os estudantes (usuários não-admin) do sistema."""
    estudantes = User.objects.filter(is_superuser=False, is_staff=False).order_by('username')
    
    if not estudantes:
        print('Nenhum estudante encontrado no sistema.')
        return
    
    print(f'\n{"="*60}')
    print(f'ESTUDANTES CADASTRADOS ({estudantes.count()})')
    print(f'{"="*60}\n')
    
    for e in estudantes:
        print(f'Matrícula: {e.username}')
        print(f'Nome: {e.first_name} {e.last_name}')
        print(f'Email: {e.email}')
        print(f'Ativo: {"Sim" if e.is_active else "Não"}')
        print(f'Último login: {e.last_login.strftime("%d/%m/%Y %H:%M") if e.last_login else "Nunca"}')
        print('-' * 60)


def criar_estudantes_exemplo():
    """Cria alguns estudantes de exemplo para teste."""
    print('\n=== CRIANDO ESTUDANTES DE EXEMPLO ===\n')
    
    estudantes = [
        ('20231001', 'joao.silva@academico.ifpb.edu.br', 'João', 'Silva'),
        ('20231002', 'maria.santos@academico.ifpb.edu.br', 'Maria', 'Santos'),
        ('20231003', 'pedro.costa@academico.ifpb.edu.br', 'Pedro', 'Costa'),
    ]
    
    for matricula, email, nome, sobrenome in estudantes:
        criar_estudante(matricula, email, nome, sobrenome)
        print()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerenciar estudantes no sistema IFTECA')
    parser.add_argument('--criar', action='store_true', help='Criar estudantes de exemplo')
    parser.add_argument('--listar', action='store_true', help='Listar todos os estudantes')
    parser.add_argument('--matricula', type=str, help='Matrícula do estudante')
    parser.add_argument('--email', type=str, help='Email do estudante')
    parser.add_argument('--nome', type=str, help='Primeiro nome do estudante')
    parser.add_argument('--sobrenome', type=str, help='Sobrenome do estudante')
    parser.add_argument('--senha', type=str, help='Senha do estudante (opcional)')
    
    args = parser.parse_args()
    
    if args.listar:
        listar_estudantes()
    elif args.criar:
        criar_estudantes_exemplo()
    elif args.matricula and args.email and args.nome and args.sobrenome:
        criar_estudante(args.matricula, args.email, args.nome, args.sobrenome, args.senha)
    else:
        print('Uso:')
        print('  python scripts/criar_estudantes.py --criar             # Criar estudantes de exemplo')
        print('  python scripts/criar_estudantes.py --listar            # Listar todos os estudantes')
        print('  python scripts/criar_estudantes.py --matricula 20231001 --email aluno@ifpb.edu.br --nome João --sobrenome Silva')
