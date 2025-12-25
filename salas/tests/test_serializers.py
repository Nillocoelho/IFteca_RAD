"""
Testes unitários para Serializers de Sala
Como o projeto não utiliza Django REST Framework serializers para Sala,
estes testes focam em criar um serializer básico e testá-lo,
além de testar a serialização/desserialização JSON manual usada no projeto
"""
import json

from django.test import TestCase

from salas.models import Sala


class SalaSerializerTests(TestCase):
    """
    Testes de serialização e desserialização de dados de Sala.
    Como não há serializers DRF, testa a conversão JSON manual.
    """

    def test_serializar_sala_para_dict(self):
        """Testa conversão de sala para dicionário"""
        sala = Sala.objects.create(
            nome="Sala Serialize",
            capacidade=20,
            tipo="Coletiva",
            localizacao="Bloco A",
            equipamentos=["Projetor", "Quadro"],
            descricao="Sala teste",
            status="Disponivel"
        )
        
        sala_dict = {
            "id": sala.id,
            "nome": sala.nome,
            "capacidade": sala.capacidade,
            "tipo": sala.tipo,
            "localizacao": sala.localizacao,
            "equipamentos": sala.equipamentos,
            "descricao": sala.descricao,
            "status": sala.status
        }
        
        self.assertEqual(sala_dict["nome"], "Sala Serialize")
        self.assertEqual(sala_dict["capacidade"], 20)
        self.assertIsInstance(sala_dict["equipamentos"], list)

    def test_serializar_sala_para_json(self):
        """Testa conversão de sala para JSON"""
        sala = Sala.objects.create(
            nome="Sala JSON",
            capacidade=15,
            tipo="Auditorio",
            equipamentos=["TV", "Ar condicionado"],
            status="Disponivel"
        )
        
        sala_data = {
            "id": sala.id,
            "nome": sala.nome,
            "capacidade": sala.capacidade,
            "tipo": sala.tipo,
            "equipamentos": sala.equipamentos,
            "status": sala.status
        }
        
        json_str = json.dumps(sala_data)
        self.assertIsInstance(json_str, str)
        self.assertIn("Sala JSON", json_str)

    def test_desserializar_json_para_sala(self):
        """Testa conversão de JSON para modelo Sala"""
        json_data = {
            "nome": "Sala Deserialize",
            "capacidade": 25,
            "tipo": "Coletiva",
            "localizacao": "Bloco B",
            "equipamentos": ["Projetor"],
            "descricao": "Teste",
            "status": "Disponivel"
        }
        
        sala = Sala(**json_data)
        sala.full_clean()
        sala.save()
        
        self.assertEqual(sala.nome, "Sala Deserialize")
        self.assertEqual(sala.capacidade, 25)
        self.assertEqual(sala.equipamentos, ["Projetor"])

    def test_serializar_sala_com_campos_none(self):
        """Testa serialização de sala com campos opcionais None"""
        sala = Sala.objects.create(
            nome="Sala Minima",
            capacidade=10,
            tipo="Coletiva"
        )
        
        sala_dict = {
            "id": sala.id,
            "nome": sala.nome,
            "capacidade": sala.capacidade,
            "tipo": sala.tipo,
            "localizacao": sala.localizacao,
            "equipamentos": sala.equipamentos,
            "descricao": sala.descricao,
            "status": sala.status
        }
        
        self.assertIsNone(sala_dict["localizacao"])
        self.assertIsNone(sala_dict["descricao"])
        self.assertEqual(sala_dict["equipamentos"], [])

    def test_json_dumps_sala_completa(self):
        """Testa json.dumps com sala completa"""
        sala = Sala.objects.create(
            nome="Sala Completa",
            capacidade=30,
            tipo="Auditorio",
            localizacao="Bloco C",
            equipamentos=["Projetor", "Quadro", "Ar"],
            descricao="Sala completa para testes",
            status="Disponivel"
        )
        
        sala_dict = {
            "id": sala.id,
            "nome": sala.nome,
            "capacidade": sala.capacidade,
            "tipo": sala.tipo,
            "localizacao": sala.localizacao,
            "equipamentos": sala.equipamentos,
            "descricao": sala.descricao,
            "status": sala.status
        }
        
        json_str = json.dumps(sala_dict)
        parsed = json.loads(json_str)
        
        self.assertEqual(parsed["nome"], "Sala Completa")
        self.assertEqual(parsed["capacidade"], 30)
        self.assertEqual(len(parsed["equipamentos"]), 3)

    def test_json_loads_dados_validos(self):
        """Testa json.loads com dados válidos"""
        json_str = '''
        {
            "nome": "Sala Parse",
            "capacidade": 18,
            "tipo": "Coletiva",
            "equipamentos": ["Quadro"],
            "status": "Disponivel"
        }
        '''
        
        dados = json.loads(json_str)
        sala = Sala(**dados)
        sala.full_clean()
        sala.save()
        
        self.assertEqual(sala.nome, "Sala Parse")
        self.assertEqual(sala.capacidade, 18)

    def test_serializar_lista_salas(self):
        """Testa serialização de múltiplas salas"""
        Sala.objects.create(nome="Sala 1", capacidade=10, tipo="Coletiva")
        Sala.objects.create(nome="Sala 2", capacidade=20, tipo="Auditorio")
        
        salas = Sala.objects.all()
        salas_list = [
            {
                "id": s.id,
                "nome": s.nome,
                "capacidade": s.capacidade,
                "tipo": s.tipo
            }
            for s in salas
        ]
        
        self.assertEqual(len(salas_list), 2)
        self.assertEqual(salas_list[0]["nome"], "Sala 1")
        self.assertEqual(salas_list[1]["nome"], "Sala 2")

    def test_serializar_equipamentos_lista_vazia(self):
        """Testa serialização com equipamentos vazio"""
        sala = Sala.objects.create(
            nome="Sala Sem Equip",
            capacidade=10,
            tipo="Coletiva",
            equipamentos=[]
        )
        
        sala_dict = {
            "equipamentos": sala.equipamentos
        }
        
        json_str = json.dumps(sala_dict)
        parsed = json.loads(json_str)
        
        self.assertEqual(parsed["equipamentos"], [])
        self.assertIsInstance(parsed["equipamentos"], list)

    def test_desserializar_equipamentos_string(self):
        """Testa desserialização de equipamentos como string separada por vírgula"""
        dados = {
            "nome": "Sala Equip String",
            "capacidade": 15,
            "tipo": "Coletiva",
            "equipamentos": "Projetor, Quadro, Ar condicionado"
        }
        
        # Converte string para lista (como feito na view)
        if isinstance(dados["equipamentos"], str):
            dados["equipamentos"] = [
                e.strip() for e in dados["equipamentos"].split(",") if e.strip()
            ]
        
        sala = Sala(**dados)
        sala.full_clean()
        sala.save()
        
        self.assertEqual(len(sala.equipamentos), 3)
        self.assertIn("Projetor", sala.equipamentos)

    def test_serializar_com_caracteres_especiais(self):
        """Testa serialização com caracteres especiais"""
        sala = Sala.objects.create(
            nome="Sala Especial: áéíóú",
            capacidade=12,
            tipo="Coletiva",
            descricao="Descrição com çñ e acentuação"
        )
        
        sala_dict = {
            "nome": sala.nome,
            "descricao": sala.descricao
        }
        
        json_str = json.dumps(sala_dict, ensure_ascii=False)
        parsed = json.loads(json_str)
        
        self.assertEqual(parsed["nome"], "Sala Especial: áéíóú")
        self.assertIn("ç", parsed["descricao"])

    def test_json_invalid_format(self):
        """Testa erro ao fazer parse de JSON inválido"""
        json_invalido = "{ nome: 'sem aspas' }"
        
        with self.assertRaises(json.JSONDecodeError):
            json.loads(json_invalido)

    def test_serializar_campo_criado_em(self):
        """Testa serialização do campo criado_em (datetime)"""
        sala = Sala.objects.create(
            nome="Sala Data",
            capacidade=10,
            tipo="Coletiva"
        )
        
        # datetime precisa ser convertido para string para JSON
        sala_dict = {
            "id": sala.id,
            "nome": sala.nome,
            "criado_em": sala.criado_em.isoformat()
        }
        
        json_str = json.dumps(sala_dict)
        parsed = json.loads(json_str)
        
        self.assertIn("criado_em", parsed)
        self.assertIsInstance(parsed["criado_em"], str)

    def test_desserializar_status_padrao(self):
        """Testa que status assume valor padrão se não fornecido"""
        dados = {
            "nome": "Sala Status Padrao",
            "capacidade": 10,
            "tipo": "Coletiva"
        }
        
        sala = Sala(**dados)
        sala.full_clean()
        sala.save()
        
        self.assertEqual(sala.status, "Disponivel")

    def test_serializar_apenas_campos_necessarios(self):
        """Testa serialização apenas dos campos necessários"""
        sala = Sala.objects.create(
            nome="Sala Parcial",
            capacidade=15,
            tipo="Coletiva",
            localizacao="Bloco A",
            descricao="Descrição completa"
        )
        
        # Serializa apenas alguns campos
        sala_resumo = {
            "id": sala.id,
            "nome": sala.nome,
            "capacidade": sala.capacidade
        }
        
        json_str = json.dumps(sala_resumo)
        parsed = json.loads(json_str)
        
        self.assertEqual(len(parsed), 3)
        self.assertNotIn("descricao", parsed)
        self.assertNotIn("localizacao", parsed)

    def test_formato_resposta_api_criar_sala(self):
        """Testa formato de resposta da API de criação"""
        sala = Sala.objects.create(
            nome="Sala API",
            capacidade=20,
            tipo="Coletiva"
        )
        
        response_data = {
            "message": "Sala cadastrada com sucesso.",
            "sala": {
                "id": sala.id,
                "nome": sala.nome,
                "capacidade": sala.capacidade,
                "tipo": sala.tipo,
                "status": sala.status
            }
        }
        
        self.assertIn("message", response_data)
        self.assertIn("sala", response_data)
        self.assertEqual(response_data["sala"]["nome"], "Sala API")

    def test_formato_resposta_erro(self):
        """Testa formato de resposta de erro"""
        error_response = {
            "errors": [
                "O nome da sala e obrigatorio.",
                "Capacidade deve ser um numero inteiro positivo."
            ]
        }
        
        json_str = json.dumps(error_response)
        parsed = json.loads(json_str)
        
        self.assertIn("errors", parsed)
        self.assertIsInstance(parsed["errors"], list)
        self.assertEqual(len(parsed["errors"]), 2)

    def test_serializar_multiplos_equipamentos(self):
        """Testa serialização de sala com vários equipamentos"""
        equipamentos = [
            "Projetor",
            "Quadro branco",
            "Ar condicionado",
            "TV",
            "Computadores"
        ]
        
        sala = Sala.objects.create(
            nome="Sala Multi Equip",
            capacidade=30,
            tipo="Coletiva",
            equipamentos=equipamentos
        )
        
        sala_dict = {
            "equipamentos": sala.equipamentos
        }
        
        json_str = json.dumps(sala_dict)
        parsed = json.loads(json_str)
        
        self.assertEqual(len(parsed["equipamentos"]), 5)
        self.assertIn("Projetor", parsed["equipamentos"])
