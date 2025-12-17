import json
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from salas.models import Sala


class SalaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.admin = User.objects.create_user(
            username="admin@example.com",
            email="admin@example.com",
            password="password123",
            is_staff=True,
        )
        cls.client = Client()

    def login_admin(self):
        self.client.force_login(self.admin)

    # CT1.1 – Cadastro com Sucesso
    def test_cadastro_sala_com_sucesso(self):
        self.login_admin()
        payload = {
            "nome": "Sala Nova",
            "capacidade": 20,
            "tipo": "Coletiva",
            "equipamentos": ["Projetor", "Quadro"],
            "status": "Disponivel",
            "descricao": "Sala para testes",
        }

        resp = self.client.post(
            reverse("api_criar_sala"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Sala.objects.filter(nome="Sala Nova").count(), 1)
        self.assertIn("Sala cadastrada", resp.json().get("message", ""))

    # CT1.2 – Tentativa de Cadastro sem Campos Obrigatórios
    def test_cadastro_sala_campos_obrigatorios(self):
        self.login_admin()
        initial_count = Sala.objects.count()
        payload = {"nome": "", "capacidade": "", "tipo": "Coletiva"}

        resp = self.client.post(
            reverse("api_criar_sala"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Sala.objects.count(), initial_count)
        errors = resp.json().get("errors", [])
        self.assertTrue(errors)

    # CT1.3 – Tentativa de Cadastro com Nome Duplicado
    def test_cadastro_sala_nome_duplicado(self):
        Sala.objects.create(nome="Sala X", capacidade=10, tipo="Coletiva")
        self.login_admin()
        initial_count = Sala.objects.count()

        payload = {"nome": "Sala X", "capacidade": 12, "tipo": "Coletiva"}
        resp = self.client.post(
            reverse("api_criar_sala"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Sala.objects.count(), initial_count)
        self.assertIn("Ja existe uma sala", " ".join(resp.json().get("errors", [])))

    # CT2.1 – Visualização da lista no painel Admin
    def test_lista_admin_renderiza_salas(self):
        Sala.objects.create(nome="Sala Admin A", capacidade=15, tipo="Coletiva")
        Sala.objects.create(nome="Sala Admin B", capacidade=18, tipo="Auditorio")
        self.login_admin()

        resp = self.client.get(reverse("gerenciar_salas"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Sala Admin A")
        self.assertContains(resp, "Sala Admin B")

    # CT2.2 – Ações de Gerenciamento Visíveis (Admin)
    def test_lista_admin_mostra_acoes_editar_e_excluir(self):
        Sala.objects.create(nome="Sala Admin C", capacidade=12, tipo="Coletiva")
        self.login_admin()

        resp = self.client.get(reverse("gerenciar_salas"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "btn-edit")
        self.assertContains(resp, "btn-delete")

    # CT3.1 – Visualização da Lista Pública
    def test_lista_publica_disponivel_para_anonimo(self):
        Sala.objects.create(nome="Sala Publica", capacidade=30, tipo="Auditorio")

        resp = self.client.get(reverse("listar_salas"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Sala Publica")

    # CT3.2 – Informações Visíveis na Lista
    def test_lista_publica_mostra_campos_principais(self):
        sala = Sala.objects.create(nome="Sala Info", capacidade=22, tipo="Coletiva")

        resp = self.client.get(reverse("listar_salas"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, sala.nome)
        self.assertContains(resp, f"{sala.capacidade} pessoas")

    # CT3.3 – Interação para Ver Disponibilidade
    def test_link_ver_disponibilidade_funciona(self):
        sala = Sala.objects.create(nome="Sala Link", capacidade=18, tipo="Coletiva", status="Disponivel")
        lista_resp = self.client.get(reverse("listar_salas"))
        self.assertEqual(lista_resp.status_code, 200)
        detalhe_url = reverse("detalhar_sala", args=[sala.id])
        self.assertContains(lista_resp, detalhe_url)

        detalhe_resp = self.client.get(detalhe_url)
        self.assertEqual(detalhe_resp.status_code, 200)
        self.assertContains(detalhe_resp, sala.nome)

    # CT4.1 – Edição com Sucesso
    def test_edicao_sala_com_sucesso(self):
        sala = Sala.objects.create(nome="Sala Edit", capacidade=10, tipo="Coletiva")
        self.login_admin()
        payload = {
            "nome": "Sala Editada",
            "capacidade": 25,
            "tipo": "Auditorio",
            "status": "Disponivel",
        }

        resp = self.client.put(
            reverse("api_update_delete_sala", args=[sala.id]),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 200)
        sala.refresh_from_db()
        self.assertEqual(sala.nome, "Sala Editada")
        self.assertEqual(sala.capacidade, 25)
        self.assertEqual(sala.tipo, "Auditorio")

    # CT5.1 – Deleção de Sala com Sucesso
    def test_delecao_sala_com_sucesso(self):
        sala = Sala.objects.create(nome="Sala Delete", capacidade=8, tipo="Coletiva")
        self.login_admin()

        resp = self.client.delete(reverse("api_update_delete_sala", args=[sala.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Sala.objects.filter(id=sala.id).exists())

    # CT5.2 – Tentativa de Excluir Sala com Reservas Futuras
    def test_tentativa_exclusao_sala_com_reservas_futuras(self):
        from reservas.models import Reserva
        
        # Cria uma sala
        sala = Sala.objects.create(nome="Sala com Reserva", capacidade=15, tipo="Coletiva")
        
        # Cria uma reserva futura para essa sala
        inicio_futuro = timezone.now() + timedelta(days=2)
        fim_futuro = inicio_futuro + timedelta(hours=2)
        
        Reserva.objects.create(
            sala=sala,
            usuario=self.admin.username,
            inicio=inicio_futuro,
            fim=fim_futuro
        )
        
        # Loga como admin e tenta deletar a sala
        self.login_admin()
        
        # Verifica que a sala existe antes da tentativa
        self.assertTrue(Sala.objects.filter(id=sala.id).exists())
        
        # Tenta deletar via endpoint que tem validação de reservas futuras
        resp = self.client.delete(reverse("deletar_sala", args=[sala.id]))
        
        # Deve retornar 400 (Bad Request) por causa da reserva futura
        self.assertEqual(resp.status_code, 400)
        
        # Verifica que a sala ainda existe (não foi deletada)
        self.assertTrue(Sala.objects.filter(id=sala.id).exists())
        
        # Verifica a mensagem de erro
        response_data = resp.json()
        self.assertIn("reservas futuras", response_data.get("detail", "").lower())
    
    # CT5.3 – Deleção de Sala com Reservas Passadas (deve permitir)
    def test_delecao_sala_com_reservas_passadas_permitida(self):
        from reservas.models import Reserva
        
        # Cria uma sala
        sala = Sala.objects.create(nome="Sala com Reserva Passada", capacidade=12, tipo="Coletiva")
        
        # Cria uma reserva passada para essa sala
        inicio_passado = timezone.now() - timedelta(days=5)
        fim_passado = inicio_passado + timedelta(hours=2)
        
        Reserva.objects.create(
            sala=sala,
            usuario=self.admin.username,
            inicio=inicio_passado,
            fim=fim_passado
        )
        
        # Loga como admin e tenta deletar a sala
        self.login_admin()
        
        # Verifica que a sala existe antes da tentativa
        self.assertTrue(Sala.objects.filter(id=sala.id).exists())
        
        # Deleta via endpoint que valida apenas reservas futuras
        resp = self.client.delete(reverse("deletar_sala", args=[sala.id]))
        
        # Deve permitir a exclusão (200 OK)
        self.assertEqual(resp.status_code, 200)
        
        # Verifica que a sala foi deletada
        self.assertFalse(Sala.objects.filter(id=sala.id).exists())

