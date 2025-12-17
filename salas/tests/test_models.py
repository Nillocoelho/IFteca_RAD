"""
Testes unitários para o modelo Sala
"""
from django.core.exceptions import ValidationError
from django.test import TestCase

from salas.models import Sala


class SalaModelTests(TestCase):
    """Testes unitários para o modelo Sala"""

    def test_criar_sala_valida(self):
        """Testa criação de uma sala com dados válidos"""
        sala = Sala.objects.create(
            nome="Sala Teste",
            capacidade=20,
            tipo="Coletiva",
            localizacao="Bloco A",
            equipamentos=["Projetor", "Quadro"],
            descricao="Sala para testes",
            status="Disponivel"
        )
        
        self.assertEqual(sala.nome, "Sala Teste")
        self.assertEqual(sala.capacidade, 20)
        self.assertEqual(sala.tipo, "Coletiva")
        self.assertEqual(sala.localizacao, "Bloco A")
        self.assertEqual(sala.equipamentos, ["Projetor", "Quadro"])
        self.assertEqual(sala.descricao, "Sala para testes")
        self.assertEqual(sala.status, "Disponivel")

    def test_sala_nome_unico(self):
        """Testa que o nome da sala deve ser único"""
        Sala.objects.create(nome="Sala Unica", capacidade=10, tipo="Coletiva")
        
        with self.assertRaises(Exception):
            Sala.objects.create(nome="Sala Unica", capacidade=15, tipo="Auditorio")

    def test_sala_capacidade_positiva(self):
        """Testa que a capacidade deve ser maior que zero"""
        sala = Sala(nome="Sala Zero", capacidade=0, tipo="Coletiva")
        
        with self.assertRaises(ValidationError) as context:
            sala.full_clean()
        
        self.assertIn('capacidade', context.exception.message_dict)

    def test_sala_capacidade_negativa(self):
        """Testa que a capacidade não pode ser negativa"""
        sala = Sala(nome="Sala Negativa", capacidade=-5, tipo="Coletiva")
        
        with self.assertRaises(ValidationError):
            sala.full_clean()

    def test_sala_tipo_choices(self):
        """Testa que o tipo deve ser uma das opções válidas"""
        sala_coletiva = Sala.objects.create(
            nome="Sala Coletiva",
            capacidade=15,
            tipo="Coletiva"
        )
        self.assertEqual(sala_coletiva.tipo, "Coletiva")
        
        sala_auditorio = Sala.objects.create(
            nome="Sala Auditorio",
            capacidade=50,
            tipo="Auditorio"
        )
        self.assertEqual(sala_auditorio.tipo, "Auditorio")

    def test_sala_status_default(self):
        """Testa que o status padrão é 'Disponivel'"""
        sala = Sala.objects.create(
            nome="Sala Padrão",
            capacidade=10,
            tipo="Coletiva"
        )
        self.assertEqual(sala.status, "Disponivel")

    def test_sala_equipamentos_default_lista_vazia(self):
        """Testa que equipamentos padrão é uma lista vazia"""
        sala = Sala.objects.create(
            nome="Sala Sem Equipamentos",
            capacidade=10,
            tipo="Coletiva"
        )
        self.assertEqual(sala.equipamentos, [])

    def test_sala_clean_trim_nome(self):
        """Testa que o método clean remove espaços do nome"""
        sala = Sala(
            nome="  Sala com Espaços  ",
            capacidade=10,
            tipo="Coletiva"
        )
        sala.full_clean()
        self.assertEqual(sala.nome, "Sala com Espaços")

    def test_sala_clean_trim_localizacao(self):
        """Testa que o método clean remove espaços da localização"""
        sala = Sala(
            nome="Sala Loc",
            capacidade=10,
            tipo="Coletiva",
            localizacao="  Bloco A  "
        )
        sala.full_clean()
        self.assertEqual(sala.localizacao, "Bloco A")

    def test_sala_clean_localizacao_vazia_vira_none(self):
        """Testa que localização vazia se torna None após clean"""
        sala = Sala(
            nome="Sala Sem Loc",
            capacidade=10,
            tipo="Coletiva",
            localizacao="   "
        )
        sala.full_clean()
        self.assertIsNone(sala.localizacao)

    def test_sala_clean_descricao_vazia_vira_none(self):
        """Testa que descrição vazia se torna None após clean"""
        sala = Sala(
            nome="Sala Sem Desc",
            capacidade=10,
            tipo="Coletiva",
            descricao="   "
        )
        sala.full_clean()
        self.assertIsNone(sala.descricao)

    def test_sala_equipamentos_deve_ser_lista(self):
        """Testa que equipamentos deve ser uma lista"""
        sala = Sala(
            nome="Sala Equipamentos",
            capacidade=10,
            tipo="Coletiva",
            equipamentos="Projetor"  # String ao invés de lista
        )
        
        with self.assertRaises(ValidationError) as context:
            sala.full_clean()
        
        self.assertIn('equipamentos', context.exception.message_dict)

    def test_sala_equipamentos_lista_de_strings(self):
        """Testa que cada equipamento deve ser uma string"""
        sala = Sala(
            nome="Sala Equip Invalido",
            capacidade=10,
            tipo="Coletiva",
            equipamentos=["Projetor", 123, "Quadro"]  # 123 não é string
        )
        
        with self.assertRaises(ValidationError) as context:
            sala.full_clean()
        
        self.assertIn('equipamentos', context.exception.message_dict)

    def test_sala_equipamentos_remove_strings_vazias(self):
        """Testa que strings vazias são removidas dos equipamentos"""
        sala = Sala(
            nome="Sala Equip Vazios",
            capacidade=10,
            tipo="Coletiva",
            equipamentos=["Projetor", "  ", "", "Quadro"]
        )
        sala.full_clean()
        self.assertEqual(sala.equipamentos, ["Projetor", "Quadro"])

    def test_sala_equipamentos_trim_strings(self):
        """Testa que espaços são removidos dos nomes de equipamentos"""
        sala = Sala(
            nome="Sala Equip Trim",
            capacidade=10,
            tipo="Coletiva",
            equipamentos=["  Projetor  ", " Quadro "]
        )
        sala.full_clean()
        self.assertEqual(sala.equipamentos, ["Projetor", "Quadro"])

    def test_sala_str_representation(self):
        """Testa a representação em string da sala"""
        sala = Sala.objects.create(
            nome="Sala 101",
            capacidade=20,
            tipo="Coletiva"
        )
        self.assertEqual(str(sala), "Sala 101 (Coletiva)")

    def test_sala_ordering(self):
        """Testa que salas são ordenadas por nome"""
        Sala.objects.create(nome="Sala C", capacidade=10, tipo="Coletiva")
        Sala.objects.create(nome="Sala A", capacidade=10, tipo="Coletiva")
        Sala.objects.create(nome="Sala B", capacidade=10, tipo="Coletiva")
        
        salas = list(Sala.objects.all())
        nomes = [sala.nome for sala in salas]
        self.assertEqual(nomes, ["Sala A", "Sala B", "Sala C"])

    def test_sala_criado_em_auto_set(self):
        """Testa que o campo criado_em é preenchido automaticamente"""
        sala = Sala.objects.create(
            nome="Sala Data",
            capacidade=10,
            tipo="Coletiva"
        )
        self.assertIsNotNone(sala.criado_em)

    def test_sala_campos_opcionais(self):
        """Testa criação de sala apenas com campos obrigatórios"""
        sala = Sala.objects.create(
            nome="Sala Minima",
            capacidade=10,
            tipo="Coletiva"
        )
        
        self.assertIsNone(sala.localizacao)
        self.assertIsNone(sala.descricao)
        self.assertEqual(sala.equipamentos, [])
        self.assertEqual(sala.status, "Disponivel")

    def test_sala_status_em_manutencao(self):
        """Testa criação de sala com status 'Em Manutencao'"""
        sala = Sala.objects.create(
            nome="Sala Manutencao",
            capacidade=10,
            tipo="Coletiva",
            status="Em Manutencao"
        )
        self.assertEqual(sala.status, "Em Manutencao")

    def test_sala_equipamentos_none_vira_lista_vazia(self):
        """Testa que equipamentos None se torna lista vazia após clean"""
        sala = Sala(
            nome="Sala None Equip",
            capacidade=10,
            tipo="Coletiva",
            equipamentos=None
        )
        sala.full_clean()
        self.assertEqual(sala.equipamentos, [])

    def test_sala_nome_max_length(self):
        """Testa o tamanho máximo do campo nome"""
        nome_longo = "A" * 255
        sala = Sala.objects.create(
            nome=nome_longo,
            capacidade=10,
            tipo="Coletiva"
        )
        self.assertEqual(len(sala.nome), 255)

    def test_sala_capacidade_minima_validator(self):
        """Testa validador de capacidade mínima"""
        sala = Sala(
            nome="Sala Cap Min",
            capacidade=1,
            tipo="Coletiva"
        )
        # Não deve lançar erro
        sala.full_clean()
        self.assertEqual(sala.capacidade, 1)
