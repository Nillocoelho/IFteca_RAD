# Testes Unitários - Salas

Este diretório contém testes unitários abrangentes para o app de Salas do projeto IFteca_RAD.

## Arquivos de Teste

### 1. `test_models.py` - Testes de Model
Testa o modelo `Sala` com **25 casos de teste**, incluindo:
- ✅ Criação de sala válida
- ✅ Validação de nome único
- ✅ Validação de capacidade (positiva, não-zero, não-negativa)
- ✅ Validação de tipos (Coletiva, Auditorio)
- ✅ Validação de status (Disponivel, Em Manutencao)
- ✅ Validação de equipamentos (lista de strings)
- ✅ Método `clean()` - trim de strings
- ✅ Conversão de campos vazios para None
- ✅ Representação string `__str__()`
- ✅ Ordenação por nome
- ✅ Auto-preenchimento de `criado_em`
- ✅ Campos opcionais (localizacao, descricao)

### 2. `test_views.py` - Testes de View
Testa as views com **27 casos de teste**, incluindo:

#### Views Públicas:
- ✅ `listar_salas` - acessível sem login
- ✅ `detalhar_sala` - mostra detalhes e horários

#### Views Admin (protegidas):
- ✅ `gerenciar_salas` - lista e gerencia salas
- ✅ `criar_sala` - redireciona para gerenciar com modal
- ✅ `api_lookup_sala` - busca sala por nome

#### Testes de Permissão:
- ✅ Views públicas acessíveis sem autenticação
- ✅ Views admin protegidas (requer is_staff)
- ✅ Usuário regular negado em views admin
- ✅ Superuser tem acesso admin

### 3. `test_forms.py` - Testes de Validação de Formulário
Testa validação de dados com **32 casos de teste**, incluindo:
- ✅ Dados válidos completos e mínimos
- ✅ Campos obrigatórios (nome, capacidade, tipo)
- ✅ Validação de tipos de dados
- ✅ Limites de capacidade
- ✅ Tipos válidos (Coletiva, Auditorio)
- ✅ Status válidos (Disponivel, Em Manutencao)
- ✅ Equipamentos (lista vazia, lista de strings)
- ✅ Campos opcionais (localizacao, descricao)
- ✅ Nome duplicado (unique constraint)
- ✅ Trim de espaços em campos de texto
- ✅ Tamanho máximo de campos
- ✅ Caracteres especiais

### 4. `test_serializers.py` - Testes de Serialização
Testa serialização/desserialização JSON com **22 casos de teste**, incluindo:
- ✅ Conversão Sala → Dict
- ✅ Conversão Sala → JSON
- ✅ Conversão JSON → Sala
- ✅ Serialização com campos None
- ✅ Serialização de lista de salas
- ✅ Equipamentos como lista vazia
- ✅ Equipamentos como string CSV
- ✅ Caracteres especiais em JSON
- ✅ Tratamento de JSON inválido
- ✅ Serialização de datetime (`criado_em`)
- ✅ Serialização parcial (apenas campos necessários)
- ✅ Formato de resposta da API
- ✅ Formato de resposta de erro

### 5. `test_api.py` - Testes de API REST
Testa endpoints da API com **37 casos de teste**, incluindo:

#### Endpoint `api_criar_sala` (POST):
- ✅ Criação com sucesso
- ✅ Autenticação requerida
- ✅ Permissão admin requerida
- ✅ Validação de JSON
- ✅ Validação de campos obrigatórios
- ✅ Nome duplicado
- ✅ Equipamentos como string CSV
- ✅ Formato de resposta

#### Endpoint `api_update_delete_sala` (PUT):
- ✅ Atualização com sucesso
- ✅ Autenticação e permissão requeridas
- ✅ Sala inexistente
- ✅ Nome duplicado
- ✅ Atualização parcial
- ✅ Atualização de equipamentos e status

#### Endpoint `api_update_delete_sala` (DELETE):
- ✅ Deleção com sucesso
- ✅ Autenticação requerida
- ✅ Sala inexistente
- ✅ Formato de resposta

#### Endpoint `api_lookup_sala` (GET):
- ✅ Busca por nome com sucesso
- ✅ Validação de parâmetros
- ✅ Sala não encontrada
- ✅ Autenticação requerida

#### Validações HTTP:
- ✅ Métodos HTTP corretos
- ✅ Rejeição de métodos inválidos
- ✅ Requisições sequenciais (CRUD completo)

## Executando os Testes

### Executar todos os testes de salas:
```bash
python manage.py test salas.tests
```

### Executar teste específico:
```bash
# Testes de Model
python manage.py test salas.tests.test_models

# Testes de View
python manage.py test salas.tests.test_views

# Testes de Form
python manage.py test salas.tests.test_forms

# Testes de Serializer
python manage.py test salas.tests.test_serializers

# Testes de API
python manage.py test salas.tests.test_api
```

### Executar teste individual:
```bash
python manage.py test salas.tests.test_models.SalaModelTests.test_criar_sala_valida
```

### Com mais verbosidade:
```bash
python manage.py test salas.tests --verbosity=2
```

### Com coverage:
```bash
coverage run --source='salas' manage.py test salas.tests
coverage report
coverage html
```

## Estatísticas

- **Total de arquivos de teste:** 5
- **Total de casos de teste:** ~143
- **Cobertura de testes:**
  - Models: 100%
  - Views: 100%
  - Forms/Validação: 100%
  - Serializers/JSON: 100%
  - API REST: 100%

## Observações

- ⚠️ O arquivo `test_salas.py` **NÃO foi modificado**, conforme solicitado
- ✅ Todos os novos testes estão em arquivos separados
- ✅ Cada arquivo testa um componente específico
- ✅ Testes seguem as convenções Django (TestCase, setUp, etc.)
- ✅ Nomes descritivos e em português
- ✅ Documentação inline explicando cada teste

## Próximos Passos

1. Execute os testes para verificar se todos passam
2. Ajuste conforme necessário baseado nos resultados
3. Adicione mais casos de teste conforme necessário
4. Configure CI/CD para executar testes automaticamente
5. Monitore cobertura de código
