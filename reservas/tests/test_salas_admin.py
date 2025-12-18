import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from salas.models import Sala


class SalasAdminApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user_model()
        self.admin = user_model.objects.create_user(
            username="admin@example.com",
            email="admin@example.com",
            password="password123",
            is_staff=True,
        )
        self.client.force_login(self.admin)

    def test_list_includes_description(self):
        Sala.objects.create(
            nome="Sala Descricao",
            capacidade=10,
            tipo="Coletiva",
            descricao="Descricao da sala",
        )

        resp = self.client.get(reverse("salas_admin"))

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data[0]["descricao"], "Descricao da sala")

    def test_update_keeps_existing_description(self):
        sala = Sala.objects.create(
            nome="Sala Editavel",
            capacidade=12,
            tipo="Auditorio",
            descricao="Descricao inicial",
        )

        payload = {
            "nome": "Sala Editada",
            "capacidade": 20,
            "tipo": "Auditorio",
            # descricao não enviada pela UI deve continuar igual
        }

        resp = self.client.put(
            reverse("atualizar_sala", args=[sala.id]),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, 200)
        sala.refresh_from_db()
        self.assertEqual(sala.nome, "Sala Editada")
        self.assertEqual(sala.descricao, "Descricao inicial")
