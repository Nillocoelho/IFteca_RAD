"""
Testes unitários para a API REST de Sala
Testa os endpoints de API JSON
"""
import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from salas.models import Sala


class SalaAPITests(TestCase):
    """Testes unitários para os endpoints da API REST de Sala"""

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

    # Testes do endpoint api_criar_sala
    def test_criar_sala_sucesso(self):
        """Testa criação de sala via API com sucesso"""
        self.login_admin()
        payload = {
            "nome": "Sala API Test",
            "capacidade": 20,
            "tipo": "Coletiva",
            "equipamentos": ["Projetor", "Quadro"],
            "status": "Disponivel",
            "descricao": "Sala teste API"
        }

        response = self.client.post(
            reverse("api_criar_sala"),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("Sala cadastrada", data["message"])
        self.assertTrue(Sala.objects.filter(nome="Sala API Test").exists())

    def test_criar_sala_sem_autenticacao(self):
        """Testa que criar sala sem autenticação é negado"""
        payload = {
            "nome": "Sala Sem Auth",
            "capacidade": 15,
            "tipo": "Coletiva"
        }

        response = self.client.post(
            reverse("api_criar_sala"),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 302)  # Redireciona para login

    def test_criar_sala_usuario_regular(self):
        """Testa que usuário regular não pode criar sala"""
        self.login_user()
        payload = {
            "nome": "Sala User",
            "capacidade": 15,
            "tipo": "Coletiva"
        }

        response = self.client.post(
            reverse("api_criar_sala"),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 302)

    def test_criar_sala_json_invalido(self):
        """Testa erro com JSON inválido"""
        self.login_admin()
        
        response = self.client.post(
            reverse("api_criar_sala"),
            data="{ invalid json }",
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("errors", data)

    def test_criar_sala_nome_vazio(self):
        """Testa erro ao criar sala com nome vazio"""
        self.login_admin()
        payload = {
            "nome": "",
            "capacidade": 20,
            "tipo": "Coletiva"
        }

        response = self.client.post(
            reverse("api_criar_sala"),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("errors", data)
        self.assertTrue(any("nome" in err.lower() for err in data["errors"]))

    def test_criar_sala_capacidade_invalida(self):
        """Testa erro ao criar sala com capacidade inválida"""
        self.login_admin()
        payload = {
            "nome": "Sala Cap Inv",
            "capacidade": 0,
            "tipo": "Coletiva"
        }

        response = self.client.post(
            reverse("api_criar_sala"),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("errors", data)

    def test_criar_sala_tipo_invalido(self):
        """Testa erro ao criar sala com tipo inválido"""
        self.login_admin()
        payload = {
            "nome": "Sala Tipo Inv",
            "capacidade": 20,
            "tipo": "TipoInvalido"
        }

        response = self.client.post(
            reverse("api_criar_sala"),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("errors", data)

    def test_criar_sala_nome_duplicado(self):
        """Testa erro ao criar sala com nome duplicado"""
        Sala.objects.create(nome="Sala Duplicada", capacidade=15, tipo="Coletiva")
        
        self.login_admin()
        payload = {
            "nome": "Sala Duplicada",
            "capacidade": 20,
            "tipo": "Auditorio"
        }

        response = self.client.post(
            reverse("api_criar_sala"),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("errors", data)
        self.assertTrue(any("existe" in err.lower() for err in data["errors"]))

    def test_criar_sala_equipamentos_string(self):
        """Testa criação de sala com equipamentos como string"""
        self.login_admin()
        payload = {
            "nome": "Sala Equip Str",
            "capacidade": 20,
            "tipo": "Coletiva",
            "equipamentos": "Projetor, Quadro, Ar condicionado"
        }

        response = self.client.post(
            reverse("api_criar_sala"),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        sala = Sala.objects.get(nome="Sala Equip Str")
        self.assertEqual(len(sala.equipamentos), 3)

    def test_criar_sala_resposta_formato(self):
        """Testa formato da resposta de sucesso"""
        self.login_admin()
        payload = {
            "nome": "Sala Formato",
            "capacidade": 25,
            "tipo": "Auditorio"
        }

        response = self.client.post(
            reverse("api_criar_sala"),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("sala", data)
        self.assertEqual(data["sala"]["nome"], "Sala Formato")

    # Testes do endpoint api_update_delete_sala (UPDATE)
    def test_atualizar_sala_sucesso(self):
        """Testa atualização de sala via API com sucesso"""
        sala = Sala.objects.create(
            nome="Sala Original",
            capacidade=15,
            tipo="Coletiva"
        )
        
        self.login_admin()
        payload = {
            "nome": "Sala Atualizada",
            "capacidade": 30,
            "tipo": "Auditorio",
            "status": "Em Manutencao"
        }

        response = self.client.put(
            reverse("api_update_delete_sala", args=[sala.id]),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        sala.refresh_from_db()
        self.assertEqual(sala.nome, "Sala Atualizada")
        self.assertEqual(sala.capacidade, 30)
        self.assertEqual(sala.tipo, "Auditorio")

    def test_atualizar_sala_sem_autenticacao(self):
        """Testa que atualizar sala sem autenticação é negado"""
        sala = Sala.objects.create(nome="Sala Test", capacidade=15, tipo="Coletiva")
        
        payload = {"nome": "Sala Nova", "capacidade": 20, "tipo": "Auditorio"}

        response = self.client.put(
            reverse("api_update_delete_sala", args=[sala.id]),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 302)

    def test_atualizar_sala_inexistente(self):
        """Testa erro ao atualizar sala inexistente"""
        self.login_admin()
        payload = {"nome": "Sala Nova", "capacidade": 20, "tipo": "Coletiva"}

        response = self.client.put(
            reverse("api_update_delete_sala", args=[9999]),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 404)

    def test_atualizar_sala_nome_duplicado(self):
        """Testa erro ao atualizar para nome duplicado"""
        Sala.objects.create(nome="Sala A", capacidade=10, tipo="Coletiva")
        sala_b = Sala.objects.create(nome="Sala B", capacidade=15, tipo="Coletiva")
        
        self.login_admin()
        payload = {
            "nome": "Sala A",
            "capacidade": 20,
            "tipo": "Auditorio"
        }

        response = self.client.put(
            reverse("api_update_delete_sala", args=[sala_b.id]),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("errors", data)

    def test_atualizar_sala_campo_parcial(self):
        """Testa atualização parcial de campos"""
        sala = Sala.objects.create(
            nome="Sala Parcial",
            capacidade=20,
            tipo="Coletiva",
            descricao="Descrição original"
        )
        
        self.login_admin()
        # Atualiza apenas alguns campos
        payload = {
            "nome": "Sala Parcial",
            "capacidade": 25,
            "tipo": "Coletiva"
        }

        response = self.client.put(
            reverse("api_update_delete_sala", args=[sala.id]),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        sala.refresh_from_db()
        self.assertEqual(sala.capacidade, 25)

    def test_atualizar_sala_equipamentos(self):
        """Testa atualização de equipamentos"""
        sala = Sala.objects.create(
            nome="Sala Equip Update",
            capacidade=20,
            tipo="Coletiva",
            equipamentos=["Projetor"]
        )
        
        self.login_admin()
        payload = {
            "nome": "Sala Equip Update",
            "capacidade": 20,
            "tipo": "Coletiva",
            "equipamentos": ["Projetor", "Quadro", "TV"]
        }

        response = self.client.put(
            reverse("api_update_delete_sala", args=[sala.id]),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        sala.refresh_from_db()
        self.assertEqual(len(sala.equipamentos), 3)

    # Testes do endpoint api_update_delete_sala (DELETE)
    def test_deletar_sala_sucesso(self):
        """Testa deleção de sala via API com sucesso"""
        sala = Sala.objects.create(
            nome="Sala Delete",
            capacidade=10,
            tipo="Coletiva"
        )
        
        self.login_admin()
        response = self.client.delete(
            reverse("api_update_delete_sala", args=[sala.id])
        )

        self.assertEqual(response.status_code, 200)
        sala.refresh_from_db()
        self.assertFalse(sala.ativo)

    def test_deletar_sala_sem_autenticacao(self):
        """Testa que deletar sala sem autenticação é negado"""
        sala = Sala.objects.create(nome="Sala Test", capacidade=15, tipo="Coletiva")
        
        response = self.client.delete(
            reverse("api_update_delete_sala", args=[sala.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Sala.objects.filter(id=sala.id).exists())

    def test_deletar_sala_inexistente(self):
        """Testa erro ao deletar sala inexistente"""
        self.login_admin()
        response = self.client.delete(
            reverse("api_update_delete_sala", args=[9999])
        )

        self.assertEqual(response.status_code, 404)

    def test_deletar_sala_resposta(self):
        """Testa formato da resposta de deleção"""
        sala = Sala.objects.create(nome="Sala Del Resp", capacidade=10, tipo="Coletiva")
        
        self.login_admin()
        response = self.client.delete(
            reverse("api_update_delete_sala", args=[sala.id])
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("id", data)

    # Testes do endpoint api_lookup_sala
    def test_lookup_sala_sucesso(self):
        """Testa busca de sala por nome com sucesso"""
        sala = Sala.objects.create(nome="Sala Lookup Test", capacidade=20, tipo="Coletiva")
        
        self.login_admin()
        response = self.client.get(
            reverse("api_lookup_sala"),
            {"nome": "Sala Lookup Test"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], sala.id)
        self.assertEqual(data["nome"], "Sala Lookup Test")

    def test_lookup_sala_sem_parametro(self):
        """Testa erro ao buscar sem parâmetro nome"""
        self.login_admin()
        response = self.client.get(reverse("api_lookup_sala"))

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("errors", data)

    def test_lookup_sala_nao_encontrada(self):
        """Testa erro quando sala não é encontrada"""
        self.login_admin()
        response = self.client.get(
            reverse("api_lookup_sala"),
            {"nome": "Sala Inexistente"}
        )

        self.assertEqual(response.status_code, 404)

    def test_lookup_sala_sem_autenticacao(self):
        """Testa que lookup sem autenticação é negado"""
        response = self.client.get(
            reverse("api_lookup_sala"),
            {"nome": "Qualquer"}
        )

        self.assertEqual(response.status_code, 302)

    # Testes de métodos HTTP
    def test_criar_sala_metodo_get_invalido(self):
        """Testa que GET não é permitido no endpoint de criar"""
        self.login_admin()
        response = self.client.get(reverse("api_criar_sala"))

        self.assertEqual(response.status_code, 405)  # Method Not Allowed

    def test_update_delete_metodo_get_invalido(self):
        """Testa que GET não é permitido no endpoint de update/delete"""
        sala = Sala.objects.create(nome="Sala Test", capacidade=15, tipo="Coletiva")
        
        self.login_admin()
        response = self.client.get(
            reverse("api_update_delete_sala", args=[sala.id])
        )

        self.assertEqual(response.status_code, 405)

    def test_lookup_sala_metodo_post_invalido(self):
        """Testa que POST não é permitido no endpoint de lookup"""
        self.login_admin()
        response = self.client.post(reverse("api_lookup_sala"))

        self.assertEqual(response.status_code, 405)

    # Testes de validação de dados
    def test_criar_sala_todos_campos_opcionais(self):
        """Testa criação com todos os campos opcionais"""
        self.login_admin()
        payload = {
            "nome": "Sala Completa API",
            "capacidade": 30,
            "tipo": "Auditorio",
            "localizacao": "Bloco A - 2º Andar",
            "equipamentos": ["Projetor", "Quadro", "Ar", "TV"],
            "descricao": "Sala completa para eventos",
            "status": "Disponivel"
        }

        response = self.client.post(
            reverse("api_criar_sala"),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        sala = Sala.objects.get(nome="Sala Completa API")
        self.assertEqual(sala.localizacao, "Bloco A - 2º Andar")
        self.assertEqual(len(sala.equipamentos), 4)

    def test_criar_sala_apenas_campos_obrigatorios(self):
        """Testa criação apenas com campos obrigatórios"""
        self.login_admin()
        payload = {
            "nome": "Sala Minima API",
            "capacidade": 10,
            "tipo": "Coletiva"
        }

        response = self.client.post(
            reverse("api_criar_sala"),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        sala = Sala.objects.get(nome="Sala Minima API")
        self.assertIsNone(sala.localizacao)
        self.assertEqual(sala.equipamentos, [])

    def test_atualizar_sala_status(self):
        """Testa atualização apenas do status"""
        sala = Sala.objects.create(
            nome="Sala Status",
            capacidade=20,
            tipo="Coletiva",
            status="Disponivel"
        )
        
        self.login_admin()
        payload = {
            "nome": "Sala Status",
            "capacidade": 20,
            "tipo": "Coletiva",
            "status": "Em Manutencao"
        }

        response = self.client.put(
            reverse("api_update_delete_sala", args=[sala.id]),
            data=json.dumps(payload),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        sala.refresh_from_db()
        self.assertEqual(sala.status, "Em Manutencao")

    def test_multiplas_requisicoes_sequenciais(self):
        """Testa múltiplas requisições em sequência"""
        self.login_admin()
        
        # Criar
        payload_criar = {
            "nome": "Sala Multi Req",
            "capacidade": 15,
            "tipo": "Coletiva"
        }
        response = self.client.post(
            reverse("api_criar_sala"),
            data=json.dumps(payload_criar),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        
        # Buscar
        sala = Sala.objects.get(nome="Sala Multi Req")
        
        # Atualizar
        payload_update = {
            "nome": "Sala Multi Req Atualizada",
            "capacidade": 25,
            "tipo": "Auditorio"
        }
        response = self.client.put(
            reverse("api_update_delete_sala", args=[sala.id]),
            data=json.dumps(payload_update),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        
        # Deletar
        response = self.client.delete(
            reverse("api_update_delete_sala", args=[sala.id])
        )
        self.assertEqual(response.status_code, 200)
        
        # Verificar que foi deletada
        sala.refresh_from_db()
        self.assertFalse(sala.ativo)
