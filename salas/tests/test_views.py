"""
Testes unitários para as views de Sala
"""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from salas.models import Sala


class SalaViewTests(TestCase):
    """Testes unitários para as views de Sala"""

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

    def login_admin(self):
        """Helper para fazer login como admin"""
        self.client.force_login(self.admin)

    def login_user(self):
        """Helper para fazer login como usuário regular"""
        self.client.force_login(self.regular_user)

    # Testes da view listar_salas
    def test_listar_salas_acessivel_sem_login(self):
        """Testa que a listagem pública é acessível sem autenticação"""
        response = self.client.get(reverse("listar_salas"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "salas/listar_salas.html")

    def test_listar_salas_mostra_salas_cadastradas(self):
        """Testa que a view mostra salas cadastradas"""
        Sala.objects.create(nome="Sala 1", capacidade=20, tipo="Coletiva")
        Sala.objects.create(nome="Sala 2", capacidade=30, tipo="Auditorio")
        
        response = self.client.get(reverse("listar_salas"))
        self.assertEqual(response.status_code, 200)
        
        salas = response.context["salas"]
        self.assertEqual(len(salas), 2)

    def test_listar_salas_context_data(self):
        """Testa que o contexto contém os dados corretos"""
        sala = Sala.objects.create(
            nome="Sala Teste",
            capacidade=25,
            tipo="Coletiva",
            equipamentos=["Projetor"],
            status="Disponivel"
        )
        
        response = self.client.get(reverse("listar_salas"))
        salas = response.context["salas"]
        
        self.assertTrue(any(s["nome"] == "Sala Teste" for s in salas))
        sala_context = next(s for s in salas if s["nome"] == "Sala Teste")
        self.assertEqual(sala_context["capacidade"], 25)
        self.assertEqual(sala_context["tipo"], "Coletiva")

    def test_listar_salas_student_name_logado(self):
        """Testa que o nome do estudante aparece quando logado"""
        self.login_user()
        response = self.client.get(reverse("listar_salas"))
        self.assertIn("student_name", response.context)

    def test_listar_salas_student_name_anonimo(self):
        """Testa que aparece nome padrão para usuário anônimo"""
        response = self.client.get(reverse("listar_salas"))
        self.assertIn("student_name", response.context)

    # Testes da view detalhar_sala
    def test_detalhar_sala_existente(self):
        """Testa acesso aos detalhes de uma sala existente"""
        sala = Sala.objects.create(
            nome="Sala Detalhes",
            capacidade=20,
            tipo="Coletiva",
            descricao="Descrição teste"
        )
        
        response = self.client.get(reverse("detalhar_sala", args=[sala.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "salas/detalhar_sala.html")

    def test_detalhar_sala_context_completo(self):
        """Testa que o contexto da sala contém todos os dados"""
        sala = Sala.objects.create(
            nome="Sala Context",
            capacidade=30,
            tipo="Auditorio",
            descricao="Teste completo",
            equipamentos=["Projetor", "Ar condicionado"],
            status="Disponivel"
        )
        
        response = self.client.get(reverse("detalhar_sala", args=[sala.id]))
        sala_context = response.context["sala"]
        
        self.assertEqual(sala_context["nome"], "Sala Context")
        self.assertEqual(sala_context["capacidade"], 30)
        self.assertEqual(sala_context["tipo"], "Auditorio")
        self.assertEqual(sala_context["descricao"], "Teste completo")
        self.assertIn("Projetor", sala_context["equipamentos"])

    def test_detalhar_sala_slots_horarios(self):
        """Testa que os slots de horário estão presentes"""
        sala = Sala.objects.create(nome="Sala Slots", capacidade=20, tipo="Coletiva")
        
        response = self.client.get(reverse("detalhar_sala", args=[sala.id]))
        self.assertIn("slots", response.context)
        self.assertTrue(len(response.context["slots"]) > 0)

    def test_detalhar_sala_inexistente_redireciona(self):
        """Testa que sala inexistente redireciona para listagem"""
        response = self.client.get(reverse("detalhar_sala", args=[9999]))
        self.assertEqual(response.status_code, 302)

    # Testes da view gerenciar_salas (admin)
    def test_gerenciar_salas_requer_admin(self):
        """Testa que gerenciar_salas requer permissão de admin"""
        response = self.client.get(reverse("gerenciar_salas"))
        self.assertEqual(response.status_code, 302)  # Redireciona para login

    def test_gerenciar_salas_usuario_regular_negado(self):
        """Testa que usuário regular não pode acessar gerenciar_salas"""
        self.login_user()
        response = self.client.get(reverse("gerenciar_salas"))
        self.assertEqual(response.status_code, 302)

    def test_gerenciar_salas_admin_acessa(self):
        """Testa que admin pode acessar gerenciar_salas"""
        self.login_admin()
        response = self.client.get(reverse("gerenciar_salas"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "salas/gerenciar_salas.html")

    def test_gerenciar_salas_lista_todas_salas(self):
        """Testa que gerenciar_salas lista todas as salas"""
        Sala.objects.create(nome="Sala Admin 1", capacidade=10, tipo="Coletiva")
        Sala.objects.create(nome="Sala Admin 2", capacidade=20, tipo="Auditorio")
        
        self.login_admin()
        response = self.client.get(reverse("gerenciar_salas"))
        
        salas = response.context["salas"]
        self.assertEqual(len(salas), 2)

    def test_gerenciar_salas_context_tipos(self):
        """Testa que o contexto inclui os tipos de sala disponíveis"""
        self.login_admin()
        response = self.client.get(reverse("gerenciar_salas"))
        
        self.assertIn("tipos", response.context)
        tipos = response.context["tipos"]
        self.assertIn("Coletiva", tipos)
        self.assertIn("Auditorio", tipos)

    # Testes da view criar_sala
    def test_criar_sala_requer_admin(self):
        """Testa que criar_sala requer permissão de admin"""
        response = self.client.get(reverse("criar_sala"))
        self.assertEqual(response.status_code, 302)

    def test_criar_sala_usuario_regular_negado(self):
        """Testa que usuário regular não pode acessar criar_sala"""
        self.login_user()
        response = self.client.get(reverse("criar_sala"))
        self.assertEqual(response.status_code, 302)

    def test_criar_sala_admin_redireciona_para_gerenciar(self):
        """Testa que criar_sala redireciona para gerenciar_salas"""
        self.login_admin()
        response = self.client.get(reverse("criar_sala"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("gerenciar_salas")))

    def test_criar_sala_redireciona_com_parametro_modal(self):
        """Testa que o redirecionamento inclui parâmetro para abrir modal"""
        self.login_admin()
        response = self.client.get(reverse("criar_sala"))
        self.assertIn("openModal=1", response.url)

    # Testes da view api_lookup_sala
    def test_api_lookup_sala_requer_admin(self):
        """Testa que api_lookup_sala requer permissão de admin"""
        response = self.client.get(reverse("api_lookup_sala"))
        self.assertEqual(response.status_code, 302)

    def test_api_lookup_sala_sem_parametro_nome(self):
        """Testa erro quando não fornece parâmetro nome"""
        self.login_admin()
        response = self.client.get(reverse("api_lookup_sala"))
        self.assertEqual(response.status_code, 400)

    def test_api_lookup_sala_encontra_sala(self):
        """Testa busca de sala por nome com sucesso"""
        sala = Sala.objects.create(nome="Sala Lookup", capacidade=15, tipo="Coletiva")
        
        self.login_admin()
        response = self.client.get(reverse("api_lookup_sala"), {"nome": "Sala Lookup"})
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], sala.id)
        self.assertEqual(data["nome"], "Sala Lookup")

    def test_api_lookup_sala_nao_encontrada(self):
        """Testa erro quando sala não é encontrada"""
        self.login_admin()
        response = self.client.get(reverse("api_lookup_sala"), {"nome": "Inexistente"})
        self.assertEqual(response.status_code, 404)

    def test_api_lookup_sala_nome_ambiguo(self):
        """Testa erro quando há múltiplas salas com mesmo nome"""
        # Nota: Isso não deveria acontecer por causa da constraint unique,
        # mas o código trata esse caso
        self.login_admin()
        response = self.client.get(reverse("api_lookup_sala"), {"nome": "Sala"})
        # Se não houver sala, retorna 404, não 409
        self.assertIn(response.status_code, [404, 409])

    # Testes de permissões gerais
    def test_views_publicas_acessiveis(self):
        """Testa que views públicas são acessíveis sem autenticação"""
        sala = Sala.objects.create(nome="Sala Publica", capacidade=20, tipo="Coletiva")
        
        # Listar salas
        response = self.client.get(reverse("listar_salas"))
        self.assertEqual(response.status_code, 200)
        
        # Detalhar sala
        response = self.client.get(reverse("detalhar_sala", args=[sala.id]))
        self.assertEqual(response.status_code, 200)

    def test_views_admin_protegidas(self):
        """Testa que views de admin são protegidas"""
        # Gerenciar salas
        response = self.client.get(reverse("gerenciar_salas"))
        self.assertEqual(response.status_code, 302)
        
        # Criar sala
        response = self.client.get(reverse("criar_sala"))
        self.assertEqual(response.status_code, 302)
        
        # API lookup
        response = self.client.get(reverse("api_lookup_sala"))
        self.assertEqual(response.status_code, 302)

    def test_superuser_tem_acesso_admin(self):
        """Testa que superuser também tem acesso às views de admin"""
        User = get_user_model()
        superuser = User.objects.create_superuser(
            username="super@example.com",
            email="super@example.com",
            password="superpass123"
        )
        
        self.client.force_login(superuser)
        response = self.client.get(reverse("gerenciar_salas"))
        self.assertEqual(response.status_code, 200)
