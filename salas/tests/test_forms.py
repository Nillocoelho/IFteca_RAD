"""
Testes unitários para Forms de Sala
Como o projeto não utiliza Django Forms tradicionais, mas validação manual nas views,
estes testes focam na validação de dados que seria feita por forms
"""
from django.test import TestCase

from salas.models import Sala


class SalaFormValidationTests(TestCase):
    """
    Testes de validação de dados de formulário para Sala.
    Simula a validação que seria feita por um Django Form.
    """

    def test_dados_validos_completos(self):
        """Testa validação de dados completos e válidos"""
        dados = {
            "nome": "Sala Teste",
            "capacidade": 20,
            "tipo": "Coletiva",
            "localizacao": "Bloco A",
            "equipamentos": ["Projetor", "Quadro"],
            "descricao": "Sala de testes",
            "status": "Disponivel"
        }
        
        sala = Sala(**dados)
        # Não deve lançar exceção
        sala.full_clean()
        sala.save()
        
        self.assertEqual(sala.nome, dados["nome"])
        self.assertEqual(sala.capacidade, dados["capacidade"])

    def test_dados_validos_minimos(self):
        """Testa validação apenas com campos obrigatórios"""
        dados = {
            "nome": "Sala Minima",
            "capacidade": 10,
            "tipo": "Coletiva"
        }
        
        sala = Sala(**dados)
        sala.full_clean()
        sala.save()
        
        self.assertEqual(sala.nome, "Sala Minima")
        self.assertEqual(sala.capacidade, 10)
        self.assertEqual(sala.tipo, "Coletiva")

    def test_nome_obrigatorio(self):
        """Testa que nome é obrigatório"""
        dados = {
            "nome": "",
            "capacidade": 10,
            "tipo": "Coletiva"
        }
        
        sala = Sala(**dados)
        with self.assertRaises(Exception):
            sala.full_clean()

    def test_nome_muito_longo(self):
        """Testa nome com mais de 255 caracteres"""
        dados = {
            "nome": "A" * 256,
            "capacidade": 10,
            "tipo": "Coletiva"
        }
        
        with self.assertRaises(Exception):
            sala = Sala(**dados)
            sala.full_clean()
            sala.save()

    def test_capacidade_obrigatoria(self):
        """Testa que capacidade é obrigatória"""
        dados = {
            "nome": "Sala Sem Cap",
            "capacidade": None,
            "tipo": "Coletiva"
        }
        
        with self.assertRaises(Exception):
            sala = Sala(**dados)
            sala.full_clean()
            sala.save()

    def test_capacidade_zero_invalida(self):
        """Testa que capacidade zero é inválida"""
        from django.core.exceptions import ValidationError
        
        dados = {
            "nome": "Sala Cap Zero",
            "capacidade": 0,
            "tipo": "Coletiva"
        }
        
        sala = Sala(**dados)
        with self.assertRaises(ValidationError):
            sala.full_clean()

    def test_capacidade_negativa_invalida(self):
        """Testa que capacidade negativa é inválida"""
        from django.core.exceptions import ValidationError
        
        dados = {
            "nome": "Sala Cap Neg",
            "capacidade": -5,
            "tipo": "Coletiva"
        }
        
        sala = Sala(**dados)
        with self.assertRaises(ValidationError):
            sala.full_clean()

    def test_capacidade_string_invalida(self):
        """Testa que capacidade como string é inválida"""
        dados = {
            "nome": "Sala Cap String",
            "capacidade": "vinte",
            "tipo": "Coletiva"
        }
        
        with self.assertRaises(Exception):
            sala = Sala(**dados)
            sala.full_clean()

    def test_tipo_obrigatorio(self):
        """Testa que tipo é obrigatório"""
        dados = {
            "nome": "Sala Sem Tipo",
            "capacidade": 10,
            "tipo": ""
        }
        
        with self.assertRaises(Exception):
            sala = Sala(**dados)
            sala.full_clean()

    def test_tipo_invalido(self):
        """Testa que tipo deve ser uma das opções válidas"""
        dados = {
            "nome": "Sala Tipo Inval",
            "capacidade": 10,
            "tipo": "TipoInvalido"
        }
        
        with self.assertRaises(Exception):
            sala = Sala(**dados)
            sala.full_clean()
            sala.save()

    def test_tipo_coletiva_valido(self):
        """Testa que tipo 'Coletiva' é válido"""
        dados = {
            "nome": "Sala Coletiva",
            "capacidade": 15,
            "tipo": "Coletiva"
        }
        
        sala = Sala(**dados)
        sala.full_clean()
        sala.save()
        self.assertEqual(sala.tipo, "Coletiva")

    def test_tipo_auditorio_valido(self):
        """Testa que tipo 'Auditorio' é válido"""
        dados = {
            "nome": "Sala Auditorio",
            "capacidade": 50,
            "tipo": "Auditorio"
        }
        
        sala = Sala(**dados)
        sala.full_clean()
        sala.save()
        self.assertEqual(sala.tipo, "Auditorio")

    def test_status_disponivel_valido(self):
        """Testa que status 'Disponivel' é válido"""
        dados = {
            "nome": "Sala Disp",
            "capacidade": 10,
            "tipo": "Coletiva",
            "status": "Disponivel"
        }
        
        sala = Sala(**dados)
        sala.full_clean()
        sala.save()
        self.assertEqual(sala.status, "Disponivel")

    def test_status_em_manutencao_valido(self):
        """Testa que status 'Em Manutencao' é válido"""
        dados = {
            "nome": "Sala Manut",
            "capacidade": 10,
            "tipo": "Coletiva",
            "status": "Em Manutencao"
        }
        
        sala = Sala(**dados)
        sala.full_clean()
        sala.save()
        self.assertEqual(sala.status, "Em Manutencao")

    def test_status_invalido(self):
        """Testa que status inválido é rejeitado"""
        dados = {
            "nome": "Sala Status Inv",
            "capacidade": 10,
            "tipo": "Coletiva",
            "status": "StatusInvalido"
        }
        
        with self.assertRaises(Exception):
            sala = Sala(**dados)
            sala.full_clean()
            sala.save()

    def test_equipamentos_lista_vazia_valida(self):
        """Testa que lista vazia de equipamentos é válida"""
        dados = {
            "nome": "Sala Sem Equip",
            "capacidade": 10,
            "tipo": "Coletiva",
            "equipamentos": []
        }
        
        sala = Sala(**dados)
        sala.full_clean()
        sala.save()
        self.assertEqual(sala.equipamentos, [])

    def test_equipamentos_lista_strings_valida(self):
        """Testa que lista de strings é válida para equipamentos"""
        dados = {
            "nome": "Sala Com Equip",
            "capacidade": 10,
            "tipo": "Coletiva",
            "equipamentos": ["Projetor", "Quadro", "Ar condicionado"]
        }
        
        sala = Sala(**dados)
        sala.full_clean()
        sala.save()
        self.assertEqual(len(sala.equipamentos), 3)

    def test_equipamentos_nao_lista_invalido(self):
        """Testa que equipamentos que não é lista é inválido"""
        from django.core.exceptions import ValidationError
        
        dados = {
            "nome": "Sala Equip String",
            "capacidade": 10,
            "tipo": "Coletiva",
            "equipamentos": "Projetor"
        }
        
        sala = Sala(**dados)
        with self.assertRaises(ValidationError):
            sala.full_clean()

    def test_equipamentos_lista_com_nao_string_invalido(self):
        """Testa que equipamentos com itens que não são strings é inválido"""
        from django.core.exceptions import ValidationError
        
        dados = {
            "nome": "Sala Equip Int",
            "capacidade": 10,
            "tipo": "Coletiva",
            "equipamentos": ["Projetor", 123, "Quadro"]
        }
        
        sala = Sala(**dados)
        with self.assertRaises(ValidationError):
            sala.full_clean()

    def test_localizacao_opcional(self):
        """Testa que localização é opcional"""
        dados = {
            "nome": "Sala Sem Loc",
            "capacidade": 10,
            "tipo": "Coletiva"
        }
        
        sala = Sala(**dados)
        sala.full_clean()
        sala.save()
        self.assertIsNone(sala.localizacao)

    def test_descricao_opcional(self):
        """Testa que descrição é opcional"""
        dados = {
            "nome": "Sala Sem Desc",
            "capacidade": 10,
            "tipo": "Coletiva"
        }
        
        sala = Sala(**dados)
        sala.full_clean()
        sala.save()
        self.assertIsNone(sala.descricao)

    def test_nome_duplicado_invalido(self):
        """Testa que nome duplicado é inválido"""
        Sala.objects.create(
            nome="Sala Unica",
            capacidade=10,
            tipo="Coletiva"
        )
        
        dados = {
            "nome": "Sala Unica",
            "capacidade": 20,
            "tipo": "Auditorio"
        }
        
        with self.assertRaises(Exception):
            sala = Sala(**dados)
            sala.full_clean()
            sala.save()

    def test_trim_espacos_nome(self):
        """Testa que espaços extras no nome são removidos"""
        dados = {
            "nome": "  Sala Com Espaços  ",
            "capacidade": 10,
            "tipo": "Coletiva"
        }
        
        sala = Sala(**dados)
        sala.full_clean()
        self.assertEqual(sala.nome, "Sala Com Espaços")

    def test_trim_espacos_localizacao(self):
        """Testa que espaços extras na localização são removidos"""
        dados = {
            "nome": "Sala Loc",
            "capacidade": 10,
            "tipo": "Coletiva",
            "localizacao": "  Bloco A  "
        }
        
        sala = Sala(**dados)
        sala.full_clean()
        self.assertEqual(sala.localizacao, "Bloco A")

    def test_trim_espacos_descricao(self):
        """Testa que espaços extras na descrição são removidos"""
        dados = {
            "nome": "Sala Desc",
            "capacidade": 10,
            "tipo": "Coletiva",
            "descricao": "  Descrição teste  "
        }
        
        sala = Sala(**dados)
        sala.full_clean()
        self.assertEqual(sala.descricao, "Descrição teste")

    def test_capacidade_valor_maximo(self):
        """Testa capacidade com valor muito alto"""
        dados = {
            "nome": "Sala Grande",
            "capacidade": 1000,
            "tipo": "Auditorio"
        }
        
        sala = Sala(**dados)
        sala.full_clean()
        sala.save()
        self.assertEqual(sala.capacidade, 1000)

    def test_caracteres_especiais_nome(self):
        """Testa nome com caracteres especiais"""
        dados = {
            "nome": "Sala 101-A (Térreo)",
            "capacidade": 15,
            "tipo": "Coletiva"
        }
        
        sala = Sala(**dados)
        sala.full_clean()
        sala.save()
        self.assertEqual(sala.nome, "Sala 101-A (Térreo)")
