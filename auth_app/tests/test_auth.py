import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class AuthTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.user_password = "password123"
        cls.user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password=cls.user_password,
            is_staff=True,  # para acessar views protegidas
        )
        cls.client = Client()

    # CT6.1 – Login com Sucesso
    def test_login_com_sucesso(self):
        resp = self.client.post(
            reverse("login"),
            data=json.dumps({"email": self.user.email, "password": self.user_password}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("_auth_user_id", self.client.session)

    # CT6.2 – Credenciais Inválidas (senha errada e usuário inexistente)
    def test_login_credenciais_invalidas_mesmo_comportamento(self):
        wrong_pass_resp = self.client.post(
            reverse("login"),
            data=json.dumps({"email": self.user.email, "password": "wrongpass"}),
            content_type="application/json",
        )
        missing_user_resp = self.client.post(
            reverse("login"),
            data=json.dumps({"email": "naoexiste@example.com", "password": "wrongpass"}),
            content_type="application/json",
        )

        self.assertEqual(wrong_pass_resp.status_code, missing_user_resp.status_code)
        self.assertEqual(wrong_pass_resp.json(), missing_user_resp.json())
        self.assertNotIn("_auth_user_id", self.client.session)

    # CT6.4 – Campos Vazios no Login
    def test_login_campos_vazios(self):
        resp = self.client.post(
            reverse("login"),
            data=json.dumps({"email": "", "password": ""}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertNotIn("_auth_user_id", self.client.session)

    # CT7.1 – Logout com Sucesso
    def test_logout_com_sucesso(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("logout"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("login_page"), resp.url)
        self.assertNotIn("_auth_user_id", self.client.session)

    # CT7.2 – Acesso a Páginas Protegidas
    def test_protegido_redireciona_para_login_quando_anonimo(self):
        resp = self.client.get(reverse("gerenciar_salas"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("login_page"), resp.url)
        self.assertIn("next=", resp.url)

    # CT7.3 – Uso do Botão "Voltar" do Navegador após Logout
    def test_acesso_protegido_depois_de_logout(self):
        self.client.force_login(self.user)
        ok_resp = self.client.get(reverse("gerenciar_salas"))
        self.assertEqual(ok_resp.status_code, 200)

        self.client.get(reverse("logout"))
        resp = self.client.get(reverse("gerenciar_salas"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("login_page"), resp.url)
