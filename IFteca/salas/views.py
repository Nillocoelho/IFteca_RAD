from django.shortcuts import render


def gerenciar_salas(request):
    salas = [
        {
            "nome": "Sala 101",
            "andar": "1º Andar - Bloco A",
            "capacidade": "20 pessoas",
            "status": "Disponível",
            "equipamentos": "Projetor",
            "cor": "success",
        },
        {
            "nome": "Sala 102",
            "andar": "1º Andar - Bloco A",
            "capacidade": "15 pessoas",
            "status": "Disponível",
            "equipamentos": "Quadro branco",
            "cor": "success",
        },
        {
            "nome": "Sala 103",
            "andar": "1º Andar - Bloco A",
            "capacidade": "30 pessoas",
            "status": "Ocupada",
            "equipamentos": "Projetor",
            "cor": "danger",
        },
        {
            "nome": "Sala 104",
            "andar": "1º Andar - Bloco A",
            "capacidade": "25 pessoas",
            "status": "Disponível",
            "equipamentos": "Ar condicionado",
            "cor": "success",
        },
        {
            "nome": "Sala 201",
            "andar": "2º Andar - Bloco A",
            "capacidade": "20 pessoas",
            "status": "Em Manutenção",
            "equipamentos": "",
            "cor": "warning",
        },
        {
            "nome": "Sala 202",
            "andar": "2º Andar - Bloco A",
            "capacidade": "20 pessoas",
            "status": "Disponível",
            "equipamentos": "Quadro branco",
            "cor": "success",
        },
        {
            "nome": "Sala 203",
            "andar": "2º Andar - Bloco A",
            "capacidade": "35 pessoas",
            "status": "Disponível",
            "equipamentos": "Projetor, Ar condicionado",
            "cor": "success",
        },
        {
            "nome": "Sala 204",
            "andar": "2º Andar - Bloco A",
            "capacidade": "20 pessoas",
            "status": "Disponível",
            "equipamentos": "Quadro branco, Projetor",
            "cor": "success",
        },
        {
            "nome": "Sala 304",
            "andar": "3º Andar - Bloco B",
            "capacidade": "15 pessoas",
            "status": "Disponível",
            "equipamentos": "",
            "cor": "success",
        },
    ]
    return render(request, "salas/gerenciar_salas.html", {"salas": salas})
