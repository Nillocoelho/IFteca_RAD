"""
Testes de paginação com Paginator do Django
"""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from salas.models import Sala


class PaginationTests(TestCase):
    """Testes de paginação nas views"""

    @classmethod
    def setUpTestData(cls):
        """Configuração inicial dos dados de teste"""
        User = get_user_model()
        cls.admin = User.objects.create_user(
            username="admin@example.com",
            email="admin@example.com",
            password="password123",
            is_staff=True,
        )
        cls.regular_user = User.objects.create_user(
            username="user@example.com",
            email="user@example.com",
            password="password123",
            is_staff=False,
        )
        cls.client = Client()

        # Criar 15 salas para testar paginação (6 por página)
        for i in range(1, 16):
            Sala.objects.create(
                nome=f"Sala {i:02d}",
                capacidade=20 + i,
                tipo="Coletiva" if i % 2 == 0 else "Auditorio",
                ativo=True
            )

    def test_listar_salas_primeira_pagina(self):
        """Testa que a primeira página mostra 6 salas"""
        response = self.client.get(reverse("listar_salas"))
        self.assertEqual(response.status_code, 200)
        
        # Verifica se o contexto tem o page_obj
        self.assertIn("page_obj", response.context)
        page_obj = response.context["page_obj"]
        
        # Primeira página deve ter 6 salas
        self.assertEqual(len(response.context["salas"]), 6)
        self.assertEqual(page_obj.number, 1)
        self.assertTrue(page_obj.has_next())
        self.assertFalse(page_obj.has_previous())

    def test_listar_salas_segunda_pagina(self):
        """Testa que a segunda página funciona corretamente"""
        response = self.client.get(reverse("listar_salas") + "?page=2")
        self.assertEqual(response.status_code, 200)
        
        page_obj = response.context["page_obj"]
        
        # Segunda página deve ter 6 salas
        self.assertEqual(len(response.context["salas"]), 6)
        self.assertEqual(page_obj.number, 2)
        self.assertTrue(page_obj.has_next())
        self.assertTrue(page_obj.has_previous())

    def test_listar_salas_ultima_pagina(self):
        """Testa que a última página mostra as salas restantes"""
        response = self.client.get(reverse("listar_salas") + "?page=3")
        self.assertEqual(response.status_code, 200)
        
        page_obj = response.context["page_obj"]
        
        # Terceira página deve ter 3 salas (15 total / 6 por página = 2 completas + 1 com 3)
        self.assertEqual(len(response.context["salas"]), 3)
        self.assertEqual(page_obj.number, 3)
        self.assertFalse(page_obj.has_next())
        self.assertTrue(page_obj.has_previous())

    def test_listar_salas_pagina_invalida(self):
        """Testa que página inválida retorna a primeira página"""
        response = self.client.get(reverse("listar_salas") + "?page=999")
        self.assertEqual(response.status_code, 200)
        
        page_obj = response.context["page_obj"]
        # Deve redirecionar para a última página
        self.assertEqual(page_obj.number, 3)

    def test_listar_salas_paginator_info(self):
        """Testa que o paginator contém as informações corretas"""
        response = self.client.get(reverse("listar_salas"))
        page_obj = response.context["page_obj"]
        
        # Verifica propriedades do paginator
        self.assertEqual(page_obj.paginator.count, 15)  # Total de salas
        self.assertEqual(page_obj.paginator.num_pages, 3)  # Número de páginas
        self.assertEqual(page_obj.paginator.per_page, 6)  # Itens por página

    def test_pagination_preserva_url_parameters(self):
        """Testa que a paginação funciona com outros parâmetros de URL"""
        # Criar salas inativas para testar filtros
        Sala.objects.create(nome="Sala Inativa", capacidade=10, tipo="Coletiva", ativo=False)
        
        response = self.client.get(reverse("listar_salas") + "?page=2")
        self.assertEqual(response.status_code, 200)
        
        # A paginação deve considerar apenas salas ativas
        page_obj = response.context["page_obj"]
        self.assertEqual(page_obj.paginator.count, 15)  # Não conta a inativa
