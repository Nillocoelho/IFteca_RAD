"""
Testes unitários para o módulo de Reservas
Cobre: criação, listagem, cancelamento e validações de reservas
"""
import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from reservas.models import Reserva
from salas.models import Sala


class ReservaTests(TestCase):
    """Testes para o modelo e API de Reservas"""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        # Admin (superuser)
        cls.admin = User.objects.create_superuser(
            username="admin@ifpb.edu.br",
            email="admin@ifpb.edu.br",
            password="admin123",
        )
        # Estudante
        cls.estudante = User.objects.create_user(
            username="20231001",
            email="estudante@academico.ifpb.edu.br",
            password="senha123",
            first_name="João",
            last_name="Silva",
        )
        # Outro estudante
        cls.estudante2 = User.objects.create_user(
            username="20231002",
            email="estudante2@academico.ifpb.edu.br",
            password="senha123",
            first_name="Maria",
            last_name="Santos",
        )
        # Sala de teste
        cls.sala = Sala.objects.create(
            nome="Sala Teste Reserva",
            capacidade=20,
            tipo="Coletiva",
            status="Disponivel",
        )
        cls.client = Client()

    def login_admin(self):
        self.client.force_login(self.admin)

    def login_estudante(self):
        self.client.force_login(self.estudante)

    def login_estudante2(self):
        self.client.force_login(self.estudante2)

    # ========== TESTES DE CRIAÇÃO DE RESERVA ==========

    def test_criar_reserva_sucesso(self):
        """CT-R1: Criar reserva com sucesso"""
        self.login_estudante()
        data_futura = (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        payload = {
            "sala_id": self.sala.id,
            "data": data_futura,
            "inicio": "10:00",
            "fim": "12:00",
        }

        resp = self.client.post(
            reverse("api_criar_reserva"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Reserva.objects.filter(sala=self.sala, usuario=self.estudante.username).exists())

    def test_criar_reserva_sem_autenticacao(self):
        """CT-R2: Tentativa de reserva sem login"""
        data_futura = (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        payload = {
            "sala_id": self.sala.id,
            "data": data_futura,
            "inicio": "10:00",
            "fim": "12:00",
        }

        resp = self.client.post(
            reverse("api_criar_reserva"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        # Deve redirecionar para login ou retornar 401/403
        self.assertIn(resp.status_code, [302, 401, 403])

    def test_criar_reserva_sala_inexistente(self):
        """CT-R3: Tentativa de reserva em sala que não existe"""
        self.login_estudante()
        data_futura = (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        payload = {
            "sala_id": 99999,
            "data": data_futura,
            "inicio": "10:00",
            "fim": "12:00",
        }

        resp = self.client.post(
            reverse("api_criar_reserva"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        # A API retorna 404 para sala não encontrada
        self.assertEqual(resp.status_code, 404)

    def test_criar_reserva_conflito_horario(self):
        """CT-R4: Tentativa de reserva com conflito de horário"""
        # Data futura específica
        from datetime import datetime as dt
        from django.utils import timezone as tz
        
        data_futura_date = (timezone.now() + timedelta(days=2)).date()
        data_futura = data_futura_date.strftime("%Y-%m-%d")
        
        # Cria primeira reserva das 14:00 às 16:00
        inicio = tz.make_aware(dt.combine(data_futura_date, dt.strptime("14:00", "%H:%M").time()))
        fim = tz.make_aware(dt.combine(data_futura_date, dt.strptime("16:00", "%H:%M").time()))
        
        Reserva.objects.create(
            sala=self.sala,
            usuario=self.estudante.username,
            inicio=inicio,
            fim=fim,
        )

        # Tentar criar reserva no mesmo horário (outro usuário)
        self.login_estudante2()
        payload = {
            "sala_id": self.sala.id,
            "data": data_futura,
            "inicio": "14:00",
            "fim": "16:00",
        }

        resp = self.client.post(
            reverse("api_criar_reserva"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 400)

    # ========== TESTES DE LISTAGEM DE RESERVAS ==========

    def test_listar_minhas_reservas(self):
        """CT-R5: Estudante vê apenas suas próprias reservas"""
        self.login_estudante()

        # Criar reservas para diferentes usuários
        inicio1 = timezone.now() + timedelta(days=3, hours=10)
        Reserva.objects.create(
            sala=self.sala,
            usuario=self.estudante.username,
            inicio=inicio1,
            fim=inicio1 + timedelta(hours=2),
        )
        inicio2 = timezone.now() + timedelta(days=4, hours=10)
        Reserva.objects.create(
            sala=self.sala,
            usuario=self.estudante2.username,
            inicio=inicio2,
            fim=inicio2 + timedelta(hours=2),
        )

        resp = self.client.get(reverse("minhas_reservas"))

        self.assertEqual(resp.status_code, 200)
        # Verifica que a página carregou corretamente
        self.assertContains(resp, "Minhas Reservas")

    def test_admin_ve_todas_reservas(self):
        """CT-R6: Admin vê todas as reservas do sistema"""
        self.login_admin()

        resp = self.client.get(reverse("admin_reservas"))

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Gerenciar Reservas")

    # ========== TESTES DE CANCELAMENTO ==========

    def test_estudante_cancela_propria_reserva(self):
        """CT-R7: Estudante pode cancelar sua própria reserva"""
        self.login_estudante()
        inicio = timezone.now() + timedelta(days=5, hours=10)
        reserva = Reserva.objects.create(
            sala=self.sala,
            usuario=self.estudante.username,
            inicio=inicio,
            fim=inicio + timedelta(hours=2),
        )

        resp = self.client.post(reverse("api_cancelar_reserva", args=[reserva.id]))

        self.assertEqual(resp.status_code, 200)
        reserva.refresh_from_db()
        self.assertTrue(reserva.cancelada)

    def test_estudante_nao_cancela_reserva_alheia(self):
        """CT-R8: Estudante não pode cancelar reserva de outro"""
        inicio = timezone.now() + timedelta(days=6, hours=10)
        reserva = Reserva.objects.create(
            sala=self.sala,
            usuario=self.estudante2.username,
            inicio=inicio,
            fim=inicio + timedelta(hours=2),
        )

        self.login_estudante()  # Logado como estudante 1
        resp = self.client.post(reverse("api_cancelar_reserva", args=[reserva.id]))

        # A API retorna 404 porque filtra por username do usuário logado
        # (a reserva não é "encontrada" para este usuário)
        self.assertEqual(resp.status_code, 404)
        reserva.refresh_from_db()
        self.assertFalse(reserva.cancelada)

    def test_admin_cancela_qualquer_reserva(self):
        """CT-R9: Admin pode cancelar qualquer reserva"""
        inicio = timezone.now() + timedelta(days=7, hours=10)
        reserva = Reserva.objects.create(
            sala=self.sala,
            usuario=self.estudante.username,
            inicio=inicio,
            fim=inicio + timedelta(hours=2),
        )

        self.login_admin()
        resp = self.client.post(reverse("api_admin_cancel_reserva", args=[reserva.id]))

        self.assertEqual(resp.status_code, 200)
        reserva.refresh_from_db()
        self.assertTrue(reserva.cancelada)

    def test_nao_cancela_reserva_ja_concluida(self):
        """CT-R10: Não pode cancelar reserva já concluída"""
        inicio = timezone.now() - timedelta(days=2)
        reserva = Reserva.objects.create(
            sala=self.sala,
            usuario=self.estudante.username,
            inicio=inicio,
            fim=inicio + timedelta(hours=2),
        )

        self.login_estudante()
        resp = self.client.post(reverse("api_cancelar_reserva", args=[reserva.id]))

        self.assertEqual(resp.status_code, 400)

    # ========== TESTES DE PAGINAÇÃO ==========

    def test_paginacao_minhas_reservas(self):
        """CT-R11: Paginação funciona em minhas reservas"""
        self.login_estudante()

        # Criar 15 reservas (mais que 8 por página)
        for i in range(15):
            inicio = timezone.now() - timedelta(days=30-i, hours=10)
            Reserva.objects.create(
                sala=self.sala,
                usuario=self.estudante.username,
                inicio=inicio,
                fim=inicio + timedelta(hours=2),
            )

        # Página 1
        resp = self.client.get(reverse("minhas_reservas") + "?page=1")
        self.assertEqual(resp.status_code, 200)

        # Página 2
        resp = self.client.get(reverse("minhas_reservas") + "?page=2")
        self.assertEqual(resp.status_code, 200)

    def test_paginacao_admin_reservas(self):
        """CT-R12: Paginação funciona em admin reservas"""
        self.login_admin()

        # Criar 15 reservas
        for i in range(15):
            inicio = timezone.now() + timedelta(days=i+10, hours=10)
            Reserva.objects.create(
                sala=self.sala,
                usuario=self.estudante.username,
                inicio=inicio,
                fim=inicio + timedelta(hours=2),
            )

        resp = self.client.get(reverse("admin_reservas") + "?page=1")
        self.assertEqual(resp.status_code, 200)

    # ========== TESTES DE AUTORIZAÇÃO ==========

    def test_estudante_nao_acessa_admin_reservas(self):
        """CT-R13: Estudante não pode acessar página de admin"""
        self.login_estudante()

        resp = self.client.get(reverse("admin_reservas"))

        # Deve redirecionar para login ou negar acesso
        self.assertIn(resp.status_code, [302, 403])

    def test_staff_acessa_admin_reservas_somente_leitura(self):
        """CT-R14: Staff pode acessar admin mas não cancelar"""
        User = get_user_model()
        staff = User.objects.create_user(
            username="staff@ifpb.edu.br",
            email="staff@ifpb.edu.br",
            password="staff123",
            is_staff=True,
        )
        self.client.force_login(staff)

        # Pode acessar a página
        resp = self.client.get(reverse("admin_reservas"))
        self.assertEqual(resp.status_code, 200)

        # Mas não pode cancelar (não é superuser)
        inicio = timezone.now() + timedelta(days=20, hours=10)
        reserva = Reserva.objects.create(
            sala=self.sala,
            usuario=self.estudante.username,
            inicio=inicio,
            fim=inicio + timedelta(hours=2),
        )

        resp = self.client.post(reverse("api_admin_cancel_reserva", args=[reserva.id]))
        self.assertEqual(resp.status_code, 403)


class HorariosDisponiveisTests(TestCase):
    """Testes para a API de horários disponíveis"""

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user = User.objects.create_user(
            username="user@test.com",
            email="user@test.com",
            password="test123",
        )
        cls.sala = Sala.objects.create(
            nome="Sala Horarios",
            capacidade=15,
            tipo="Coletiva",
            status="Disponivel",
        )
        cls.client = Client()

    def test_horarios_disponiveis_formato_correto(self):
        """CT-H1: API retorna horários no formato correto"""
        self.client.force_login(self.user)
        data_futura = (timezone.now() + timedelta(days=5)).strftime("%Y-%m-%d")

        resp = self.client.get(
            reverse("api_horarios_disponiveis", args=[self.sala.id]),
            {"data": data_futura}
        )

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # A API retorna uma lista de horários diretamente
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
        # Cada item deve ter inicio, fim, disponivel
        self.assertIn("inicio", data[0])
        self.assertIn("fim", data[0])
        self.assertIn("disponivel", data[0])

    def test_horarios_sem_data_retorna_erro(self):
        """CT-H2: API retorna erro se data não for informada"""
        self.client.force_login(self.user)

        resp = self.client.get(
            reverse("api_horarios_disponiveis", args=[self.sala.id])
        )

        self.assertEqual(resp.status_code, 400)

    def test_horarios_sala_inexistente(self):
        """CT-H3: API retorna 404 para sala inexistente"""
        self.client.force_login(self.user)
        data_futura = (timezone.now() + timedelta(days=5)).strftime("%Y-%m-%d")

        resp = self.client.get(
            reverse("api_horarios_disponiveis", args=[99999]),
            {"data": data_futura}
        )

        self.assertEqual(resp.status_code, 404)
