# 🎓 IFTECA - Sistema de Reserva de Salas
## Apresentação Final - RAD (Rápido Desenvolvimento de Aplicações)

---

## 📦 1. COMANDOS DOCKER (Rodar do Zero)

### 1.1 Clonar e Iniciar o Projeto
```bash
# Clonar o repositório
git clone https://github.com/Nillocoelho/IFteca_RAD.git
cd IFteca_RAD

# Construir e iniciar os containers
docker-compose up --build -d

# Verificar se está rodando
docker ps
```

### 1.2 Configuração Inicial do Banco de Dados
```bash
# Aplicar migrações
docker exec ifteca_rad-web-1 python manage.py migrate

# Criar superusuário administrador
docker exec -it ifteca_rad-web-1 python manage.py createsuperuser
# Email: admin@ifpb.edu.br
# Senha: admin123

# Popular banco com dados de exemplo (opcional)
docker exec ifteca_rad-web-1 python scripts/popular_banco_faker.py
```

### 1.3 Executar Testes
```bash
# Rodar todos os 169 testes
docker exec ifteca_rad-web-1 python manage.py test

# Rodar testes com detalhes
docker exec ifteca_rad-web-1 python manage.py test --verbosity=2
```

### 1.4 Acessar a Aplicação
```
URL: http://localhost:8000
```

---

## 👤 2. CREDENCIAIS DE ACESSO

### 2.1 Administrador
| Campo | Valor |
|-------|-------|
| Email | `admin@ifpb.edu.br` |
| Senha | `admin123` |
| Acesso | Dashboard, Gerenciar Salas, Usuários e Reservas |

### 2.2 Estudante (exemplos do banco populado)
| Email | Matrícula | Senha |
|-------|-----------|-------|
| `joao.silva@academico.ifpb.edu.br` | 20231001 | `senha123` |
| `maria.santos@academico.ifpb.edu.br` | 20231002 | `senha123` |
| `pedro.costa@academico.ifpb.edu.br` | 20231003 | `senha123` |

---

## 🏗️ 3. FUNCIONALIDADES IMPLEMENTADAS

---

### 3.1 📐 ARQUITETURA MVT (Model-View-Template)

O Django segue o padrão **MVT**, uma variação do MVC:

#### **Models (Modelos)** - Camada de Dados
```
📁 salas/models.py      → Modelo Sala (nome, capacidade, tipo, equipamentos, status)
📁 reservas/models.py   → Modelo Reserva (sala, usuario, inicio, fim, cancelada)
📁 auth (Django)        → Modelo User (autenticação padrão do Django)
```

**Exemplo de Model:**
```python
# salas/models.py
class Sala(models.Model):
    nome = models.CharField(max_length=100)
    capacidade = models.PositiveIntegerField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    equipamentos = models.JSONField(default=list)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)  # Soft delete
```

#### **Views (Visões)** - Camada de Lógica
```
📁 salas/views.py       → Lógica de CRUD de salas, listagem pública
📁 reservas/views.py    → Lógica de reservas, dashboard, admin
📁 auth_app/views.py    → Lógica de autenticação (login/logout)
```

**Exemplo de View:**
```python
# reservas/views.py
@staff_member_required(login_url='/login/')
def admin_reservas(request):
    reservas = Reserva.objects.select_related('sala').all().order_by('-inicio')
    paginator = Paginator(reservas, 8)  # Paginação
    page_obj = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'reservas/admin_reservas.html', {'reservas': page_obj})
```

#### **Templates (Modelos de Apresentação)** - Camada de Interface
```
📁 salas/templates/salas/           → Templates de salas
📁 reservas/templates/reservas/     → Templates de reservas e admin
📁 auth_app/templates/auth_app/     → Template de login
```

**Exemplo de Template:**
```html
<!-- reservas/templates/reservas/admin_reservas.html -->
{% for r in reservas %}
  <tr>
    <td>{{ r.usuario_nome }}</td>
    <td>{{ r.obj.sala.nome }}</td>
    <td>{{ r.obj.inicio|date:"d/m/Y" }}</td>
  </tr>
{% endfor %}
```

---

### 3.2 📄 PAGINAÇÃO

Implementada com **Django Paginator** em todas as telas administrativas:

#### **Backend (Views)**
```python
# reservas/views.py - Exemplo em salas_admin
from django.core.paginator import Paginator

def salas_admin(request):
    salas = Sala.objects.filter(ativo=True).order_by('nome')
    paginator = Paginator(salas, 8)  # 8 itens por página
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    response_data = {
        "salas": [serialize_sala(s) for s in page_obj],
        "pagination": {
            "current_page": page_obj.number,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
        }
    }
    return JsonResponse(response_data)
```

#### **Frontend (JavaScript)**
```javascript
// reservas/static/reservas/gerenciar_salas.js
function renderPagination(pagination) {
    const { current_page, total_pages, has_previous, has_next } = pagination;
    // Renderiza controles de navegação
}
```

#### **Telas com Paginação (8 itens/página)**
| Tela | Arquivo View | Paginação |
|------|--------------|-----------|
| Gerenciar Salas | `reservas/views.py:salas_admin` | ✅ 8 por página |
| Gerenciar Reservas | `reservas/views.py:admin_reservas` | ✅ 8 por página |
| Gerenciar Usuários | `reservas/views.py:gerenciar_usuarios` | ✅ 8 por página |
| Minhas Reservas | `reservas/views.py:minhas_reservas` | ✅ 8 por página |

---

### 3.3 🔐 AUTENTICAÇÃO

Implementada com **Django Authentication** + **Token Authentication (DRF)**:

#### **Arquivos Principais**
```
📁 auth_app/views.py        → LoginView, logout_view
📁 auth_app/serializers.py  → LoginSerializer (validação)
📁 auth_app/urls.py         → Rotas de autenticação
```

#### **Fluxo de Login**
```python
# auth_app/serializers.py
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = authenticate(username=attrs['email'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError("Credenciais inválidas")
        attrs['user'] = user
        return attrs
```

```python
# auth_app/views.py
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)  # Sessão Django
        token, _ = Token.objects.get_or_create(user=user)  # Token DRF
        return Response({"token": token.key, "redirect_url": redirect_url})
```

#### **Testes de Autenticação (6 testes)**
```
✅ test_login_com_sucesso
✅ test_login_credenciais_invalidas_mesmo_comportamento
✅ test_login_campos_vazios
✅ test_logout_com_sucesso
✅ test_protegido_redireciona_para_login_quando_anonimo
✅ test_acesso_protegido_depois_de_logout
```

---

### 3.4 🛡️ AUTORIZAÇÃO

Implementada com **Decorators** e verificações de permissão:

#### **Níveis de Acesso**
| Nível | Verificação | Acesso |
|-------|-------------|--------|
| **Público** | Nenhuma | Listar salas, ver detalhes |
| **Estudante** | `@login_required` | Fazer reservas, ver minhas reservas |
| **Staff** | `@staff_member_required` | Visualizar admin (somente leitura) |
| **Admin** | `is_superuser` | CRUD completo, cancelar reservas |

#### **Implementação**
```python
# reservas/views.py
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required(login_url='/login/')
def admin_reservas(request):
    is_admin = request.user.is_superuser  # Só admin pode cancelar
    return render(request, 'admin_reservas.html', {'is_admin': is_admin})
```

```python
# Verificação em API de exclusão
def deletar_sala(request, sala_id):
    if not request.user.is_superuser:
        return JsonResponse({"detail": "Apenas administradores..."}, status=403)
```

#### **Proteção no Frontend**
```html
<!-- Templates verificam permissão -->
{% if is_admin %}
    <button class="btn-delete">Excluir</button>
{% else %}
    <button class="btn-disabled" disabled>Excluir</button>
{% endif %}
```

---

### 3.5 🌐 API REST com Django REST Framework

#### **Configuração**
```python
# ifteca_project/settings.py
INSTALLED_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ]
}
```

#### **Endpoints da API**
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/salas/` | Listar salas públicas |
| `GET` | `/salas/<id>/` | Detalhar sala |
| `POST` | `/salas/criar/` | Criar sala (admin) |
| `PUT` | `/salas/<id>/` | Atualizar sala (admin) |
| `DELETE` | `/salas/<id>/delete/` | Excluir sala (admin) |
| `GET` | `/reservas/admin/salas/` | Listar salas admin (paginado) |
| `POST` | `/reservas/criar/` | Criar reserva |
| `GET` | `/reservas/minhas/` | Listar minhas reservas |
| `GET` | `/api/horarios/<sala_id>/` | Horários disponíveis |

#### **Exemplo de Serializer**
```python
# salas/serializers.py (implícito na view)
def serialize_sala(sala):
    return {
        "id": sala.id,
        "nome": sala.nome,
        "capacidade": sala.capacidade,
        "tipo": sala.tipo,
        "equipamentos": sala.equipamentos,
        "status": sala.status_text,
        "descricao": sala.descricao,
    }
```

#### **Exemplo de Resposta JSON**
```json
{
  "salas": [
    {
      "id": 1,
      "nome": "Sala 101",
      "capacidade": 30,
      "tipo": "Coletiva",
      "equipamentos": ["Projetor", "Quadro"],
      "status": "Disponivel"
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 3,
    "total_items": 17,
    "has_next": true,
    "has_previous": false
  }
}
```

---

### 3.6 📨 NOTIFICACOES POR EMAIL (GMAIL)

- Envio automatico via SMTP Gmail (TLS na porta 587) com senha de app (`SMTP_USER`, `SMTP_PASS`, `SMTP_HOST`, `SMTP_PORT`).
- Destinatario fixo para evitar spam em ambiente academico: `coelho.danillo@academico.ifpb.edu.br` (ajustavel via `RESERVA_EMAIL_DESTINO` no `.env`).
- Disparos na criacao da reserva (confirmacao) e no cancelamento, inclusive cancelamentos feitos por administradores.
- Implementacao centralizada em `reservas/email_service.py`; falhas de envio sao logadas sem bloquear a operacao do usuario.

---

### 3.7 🧪 TESTES AUTOMATIZADOS

#### **Resumo dos Testes**
```
Total: 169 testes
Status: ✅ Todos passando
```

#### **Organização dos Testes**
```
📁 auth_app/tests/
   └── test_auth.py          → 6 testes de autenticação

📁 salas/tests/
   ├── test_api.py           → 40+ testes de API REST
   ├── test_models.py        → Testes de modelos
   ├── test_views.py         → Testes de views
   ├── test_serializers.py   → Testes de serialização
   ├── test_forms.py         → Testes de formulários
   └── test_salas.py         → Testes de CRUD

📁 reservas/tests/
   ├── test_salas_admin.py   → Testes de admin de salas
   └── test_reservas.py      → 21 testes de reservas
```

#### **Categorias de Testes**
| Categoria | Quantidade | Exemplos |
|-----------|------------|----------|
| **Autenticação** | 6 | Login, logout, proteção de rotas |
| **CRUD Salas** | 40+ | Criar, ler, atualizar, excluir |
| **Validações** | 20+ | Campos obrigatórios, duplicados |
| **Autorização** | 15+ | Permissões admin/staff/user |
| **Paginação** | 10+ | Navegação, limites |
| **API REST** | 30+ | Endpoints, JSON, status codes |
| **Reservas** | 21 | Criar, cancelar, conflitos, permissões, emails |

#### **Testes de Reservas (Detalhado)**
| Código | Descrição |
|--------|-----------|
| CT-R1 | Criar reserva com sucesso |
| CT-R2 | Tentativa de reserva sem login |
| CT-R3 | Tentativa de reserva em sala inexistente |
| CT-R4 | Tentativa de reserva com conflito de horário |
| CT-R4b | Email enviado ao criar reserva |
| CT-R5 | Estudante vê apenas suas próprias reservas |
| CT-R6 | Admin vê todas as reservas |
| CT-R7 | Estudante pode cancelar sua própria reserva |
| CT-R7b | Email enviado ao cancelar reserva |
| CT-R8 | Estudante não pode cancelar reserva de outro |
| CT-R9 | Admin pode cancelar qualquer reserva |
| CT-R10 | Não pode cancelar reserva já concluída |
| CT-R11 | Paginação funciona em minhas reservas |
| CT-R12 | Paginação funciona em admin reservas |
| CT-R13 | Estudante não pode acessar página de admin |
| CT-R14 | Staff pode acessar admin mas não cancelar |
| CT-H1 | API retorna horários no formato correto |
| CT-H2 | API retorna erro se data não for informada |
| CT-H3 | API retorna 404 para sala inexistente |

#### **Comando para Executar**
```bash
# Todos os testes
docker exec ifteca_rad-web-1 python manage.py test

# Testes específicos
docker exec ifteca_rad-web-1 python manage.py test auth_app
docker exec ifteca_rad-web-1 python manage.py test salas
docker exec ifteca_rad-web-1 python manage.py test reservas

# Com cobertura detalhada
docker exec ifteca_rad-web-1 python manage.py test --verbosity=2
```

---

## 🖥️ 4. TELAS DO SISTEMA

### 4.1 Telas de Administrador
| Tela | URL | Funcionalidade |
|------|-----|----------------|
| Dashboard | `/reservas/admin/dashboard/` | Estatísticas e gráficos |
| Gerenciar Salas | `/reservas/admin/salas-ui/` | CRUD de salas |
| Gerenciar Usuários | `/reservas/admin/usuarios/` | Ver/ativar usuários |
| Gerenciar Reservas | `/reservas/admin/reservas/` | Visualizar/cancelar reservas |

### 4.2 Telas de Estudante
| Tela | URL | Funcionalidade |
|------|-----|----------------|
| Minhas Reservas | `/reservas/minhas/` | Ver e cancelar reservas |
| Listar Salas | `/salas/` | Buscar salas disponíveis |
| Detalhar Sala | `/salas/<id>/` | Ver horários e reservar |
| Confirmação | `/reservas/confirmacao/<id>/` | Confirmar reserva |

---

## 📊 5. TECNOLOGIAS UTILIZADAS

| Tecnologia | Versão | Uso |
|------------|--------|-----|
| Python | 3.12 | Backend |
| Django | 5.1.3 | Framework Web |
| Django REST Framework | 3.14+ | API REST |
| Bootstrap | 5.3.3 | Frontend CSS |
| Bootstrap Icons | 1.11.3 | Ícones |
| Chart.js | 4.x | Gráficos do Dashboard |
| jsPDF | 2.x | Geração de PDF |
| Docker | Latest | Containerização |
| SQLite | 3 | Banco de Dados |

---

## 🚀 6. DEMONSTRAÇÃO RÁPIDA

### Passo 1: Iniciar
```bash
docker-compose up -d
```

### Passo 2: Acessar como Admin
1. Acesse `http://localhost:8000`
2. Login: `admin@ifpb.edu.br` / `admin123`
3. Explore: Dashboard → Salas → Usuários → Reservas

### Passo 3: Acessar como Estudante
1. Logout do admin
2. Login: `joao.silva@academico.ifpb.edu.br` / `senha123`
3. Explore: Minhas Reservas → Listar Salas → Fazer Reserva

### Passo 4: Rodar Testes
```bash
docker exec ifteca_rad-web-1 python manage.py test
# Resultado esperado: OK (169 testes)
```

---

**Desenvolvido para a disciplina de RAD - IFPB**