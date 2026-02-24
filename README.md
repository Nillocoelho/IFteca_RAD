<div align="center">

# 📚 IFteca — Sistema Inteligente de Reserva de Salas

### Gerencie salas de estudo, laboratórios e auditórios com controle de acesso, dashboard analítico e notificações por e-mail.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django%20REST%20Framework-3.15-ff1709?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Testes-169%20passando-brightgreen?logo=pytest&logoColor=white)](#-testes)
[![License](https://img.shields.io/badge/Licença-Acadêmico-yellow)](#-licença)

**[Instalação](#-quick-start)** · **[Funcionalidades](#-funcionalidades)** · **[Arquitetura](#-arquitetura)** · **[API](#-api-rest)** · **[Testes](#-testes)**

</div>

---

## 🎯 Sobre o Projeto

O **IFteca** é um sistema web full stack desenvolvido para o **IFPB** que resolve o problema de gestão e agendamento de salas em instituições de ensino. Com ele, estudantes reservam salas de forma autônoma e administradores gerenciam todo o ecossistema de espaços por meio de um painel completo com KPIs, gráficos e exportação de relatórios em PDF.

> **Projeto acadêmico da disciplina de RAD (Rápido Desenvolvimento de Aplicações) — IFPB**  
> Equipe: Danillo Coelho Barbosa · Pedro Henrique Barbosa · Cássia Dos Santos · Raiza Tomazoni

### Problema Resolvido

Em muitas instituições de ensino, o agendamento de salas de estudo e laboratórios é feito de forma manual, por planilhas ou anotações. Isso gera conflitos de horário, ociosidade de espaços e falta de visibilidade para a gestão. O IFteca digitaliza todo esse fluxo com validação automática de conflitos, notificações e indicadores em tempo real.

---

## ✨ Funcionalidades

### 👨‍🎓 Área do Estudante
- 🔍 **Busca de salas** com filtros por tipo, capacidade e equipamentos
- 📅 **Reserva de horários** com detecção automática de conflitos (mesma sala ou mesmo usuário)
- 📋 **Minhas Reservas** — visualização do histórico e cancelamento com um clique
- 📧 **Notificações por e-mail** (SMTP/Gmail) na confirmação e no cancelamento
- 🔐 **Autenticação segura** com sessão + token (DRF), CSRF e expiração automática

### 🛠️ Painel Administrativo
- 📊 **Dashboard analítico** com KPIs em tempo real:
  - Total de reservas com variação % mensal
  - Taxa de ocupação (últimas 4 semanas)
  - Salas disponíveis vs. em manutenção
  - Usuários ativos (estudantes vs. professores)
- 📈 **Gráficos interativos** (Chart.js) — reservas por mês e top 5 salas mais utilizadas
- 📄 **Exportação de relatórios em PDF** (jsPDF)
- 🏢 **CRUD completo de salas** com soft delete, equipamentos (JSON) e status
- 👥 **Gestão de usuários** — criar, ativar/desativar (com proteção contra auto-desativação)
- ❌ **Cancelamento de reservas** de qualquer usuário com notificação automática

### 🔒 Segurança
- Rate limiting no login (5 req/min por IP via `django-ratelimit`)
- Proteção CSRF em todas as operações de escrita
- Sessão com expiração (30 min) e renovação a cada requisição
- Separação rigorosa de papéis: **Estudante → Staff → Admin**

---

## 🏗️ Arquitetura

O projeto segue o padrão **MVT (Model-View-Template)** do Django, organizado em **3 apps desacoplados** + projeto raiz:

```
IFteca_RAD/
├── ifteca_project/        # Configuração central (settings, URLs, WSGI/ASGI)
├── auth_app/              # Autenticação (login/logout, token DRF, rate limit)
├── salas/                 # Modelos e views de salas (CRUD, listagem pública)
├── reservas/              # Reservas, dashboard, APIs admin, e-mail service
├── scripts/               # Faker, manutenção de dados, utilitários
├── data/                  # SQLite (persistência via Docker volume)
├── Dockerfile             # Python 3.12-slim
└── docker-compose.yml     # Orquestração com volume e variáveis de ambiente
```

### Modelos de Dados

```
┌───────────────────────┐      ┌─────────────────────────┐      ┌──────────────┐
│        Sala            │      │        Reserva           │      │  User (auth) │
├───────────────────────┤      ├─────────────────────────┤      ├──────────────┤
│ nome (unique ativa)   │◄─────│ sala (FK, PROTECT)      │      │ username     │
│ capacidade (≥1)       │      │ usuario (CharField)     │──────│ email        │
│ tipo (Coletiva /      │      │ inicio (DateTime)       │      │ is_staff     │
│       Auditório)      │      │ fim (DateTime)          │      │ is_superuser │
│ equipamentos (JSON)   │      │ cancelada (bool)        │      │ is_active    │
│ status (Disp./Manut.) │      └─────────────────────────┘      └──────────────┘
│ ativo (soft delete)   │
│ localizacao           │
│ descricao             │
└───────────────────────┘
```

**Decisões técnicas relevantes:**
- **Soft delete** em `Sala` (campo `ativo`) para preservar o histórico de reservas
- **`PROTECT`** na FK de `Reserva → Sala` para impedir exclusão acidental de salas com reservas
- **Constraint parcial** (`unique_nome_sala_ativa`) garante unicidade de nomes apenas entre salas ativas
- **Cancelamento lógico** em reservas (campo `cancelada`) ao invés de deleção

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologias |
|--------|-------------|
| **Backend** | Python 3.12 · Django 5.1 · Django REST Framework 3.15 |
| **Frontend** | Bootstrap 5.3 · Bootstrap Icons 1.11 · JavaScript ES6+ |
| **Visualização** | Chart.js 4.x (gráficos interativos) · jsPDF 2.x (relatórios PDF) |
| **Banco de Dados** | SQLite 3 (dev) — preparado para PostgreSQL via `DATABASES` |
| **Infraestrutura** | Docker · Docker Compose · SMTP Gmail (notificações) |
| **Segurança** | django-ratelimit · CSRF · Token Auth · Session Auth |
| **Dev Tools** | Faker (dados sintéticos pt_BR) · django-livereload · Logging |

---

## 🚀 Quick Start

### Opção 1 — Docker (recomendado)

```bash
# Clonar o repositório
git clone https://github.com/Nillocoelho/IFteca_RAD.git
cd IFteca_RAD

# Subir os containers
docker compose up --build -d

# Aplicar migrações e criar superusuário
docker compose exec web python manage.py migrate
docker compose exec -it web python manage.py createsuperuser

# Popular com dados de exemplo (15 salas, 30 estudantes, 8 profs, 200 reservas)
docker compose exec web python scripts/popular_banco_faker.py
```

### Opção 2 — Local (Python)

```bash
git clone https://github.com/Nillocoelho/IFteca_RAD.git
cd IFteca_RAD

python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
# source .venv/bin/activate    # Linux/macOS

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

🌐 Acesse: **http://localhost:8000**

### Credenciais de Exemplo (após popular com Faker)

| Perfil | E-mail | Senha |
|--------|--------|-------|
| 🔴 **Admin** | `admin@ifpb.edu.br` | `admin123` |
| 🟢 **Estudante** | `joao.silva@academico.ifpb.edu.br` | `senha123` |
| 🟢 **Estudante** | `maria.santos@academico.ifpb.edu.br` | `senha123` |

---

## 🌐 API REST

O sistema expõe uma **API RESTful completa** com autenticação via Token e Session:

### Autenticação
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/auth/login/` | Login (retorna token + redirect) |
| `POST` | `/api/auth/logout/` | Logout |

### Salas
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/salas/` | Listar salas públicas (paginado, 8/página) |
| `GET` | `/salas/<id>/` | Detalhe da sala + agenda de slots |
| `POST` | `/api/salas/` | Criar sala *(admin)* |
| `PUT` | `/api/salas/<id>/` | Atualizar sala *(admin)* |
| `DELETE` | `/api/salas/<id>/` | Soft delete de sala *(admin)* |

### Reservas
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/salas/<id>/horarios/?data=YYYY-MM-DD` | Horários disponíveis |
| `POST` | `/api/reservas/criar/` | Criar reserva *(estudante)* |
| `GET` | `/reservas/minhas-reservas/` | Minhas reservas (paginado) |
| `POST` | `/reservas/api/reservas/<id>/cancelar/` | Cancelar própria reserva |

### Dashboard (Admin)
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/reservas/api/dashboard/` | KPIs + dados de gráficos (JSON) |
| `GET` | `/reservas/admin/dashboard/` | Dashboard visual completo |

<details>
<summary>📋 Ver todos os 23+ endpoints</summary>

| Rota | Descrição |
|------|-----------|
| `/reservas/admin/salas/` | API paginada de salas (admin) |
| `/reservas/admin/salas/<id>/` | Atualizar sala (admin) |
| `/reservas/admin/salas/<id>/delete/` | Deletar sala (admin) |
| `/reservas/admin/salas/manage/` | UI de gestão de salas |
| `/reservas/admin/reserva/` | Gestão de reservas com filtros + paginação |
| `/reservas/admin/reservas/<id>/cancelar/` | Cancelar qualquer reserva (admin) |
| `/reservas/admin/usuarios/` | Gestão de usuários (listar, buscar) |
| `/reservas/admin/usuarios/<id>/toggle/` | Ativar/desativar usuário |
| `/reservas/admin/usuarios/criar/` | Criar novo staff/admin |
| `/reservas/confirmacao-reserva/` | Tela de confirmação |
| `/reservas/reserva/<id>/` | Detalhes da reserva |
| `/api/salas/lookup/` | Busca sala por nome |

</details>

---

## 🧪 Testes

**169 testes automatizados** cobrindo todo o fluxo do sistema (~2.300 linhas de testes):

```bash
# Rodar todos os testes
python manage.py test

# Com verbosidade
python manage.py test --verbosity=2

# Por módulo
python manage.py test auth_app salas reservas
```

### Cobertura por Módulo

| Módulo | Testes | O que cobre |
|--------|--------|-------------|
| **auth_app** | 6 | Login, logout, proteção de rotas, credenciais inválidas |
| **salas** | 100+ | CRUD, validações, API REST, serializers, paginação, soft delete |
| **reservas** | 21+ | Criar/cancelar reserva, conflitos, permissões, e-mails, paginação |

### Principais Cenários Validados

| ID | Cenário de Teste |
|----|-----------------|
| CT-R1 | ✅ Criar reserva com sucesso + e-mail de confirmação |
| CT-R4 | ✅ Rejeitar reserva com conflito de horário |
| CT-R7 | ✅ Estudante cancela sua própria reserva + e-mail |
| CT-R8 | ✅ Estudante **não** pode cancelar reserva de outro |
| CT-R9 | ✅ Admin pode cancelar qualquer reserva |
| CT-R14 | ✅ Staff visualiza admin mas não cancela reservas de outros |

---

## 👥 Perfis de Acesso

| Perfil | Reservar | Gerenciar Salas | Dashboard | Cancelar Outros |
|--------|:--------:|:---------------:|:---------:|:---------------:|
| **Estudante** | ✅ | ❌ | ❌ | ❌ |
| **Professor** | ✅ | ❌ | ❌ | ❌ |
| **Staff** | ❌ | 👁️ leitura | ✅ | ❌ |
| **Admin** | ❌ | ✅ completo | ✅ | ✅ |

> Admins e Staff são impedidos de criar reservas para si mesmos — garantindo separação de responsabilidades.

---

## 📂 Estrutura Detalhada

```
IFteca_RAD/
│
├── auth_app/                    # 🔐 App de autenticação
│   ├── views.py                 #    LoginView (DRF APIView) + logout
│   ├── serializers.py           #    LoginSerializer com validação
│   ├── templates/auth_app/      #    Tela de login responsiva
│   └── tests/                   #    6 testes de autenticação
│
├── salas/                       # 🏢 App de gestão de salas
│   ├── models.py                #    Modelo Sala (soft delete, constraints)
│   ├── views.py                 #    7 views (CRUD + API + listagem pública)
│   ├── templates/salas/         #    4 templates (listar, detalhar, gerenciar, criar)
│   └── tests/                   #    100+ testes (API, models, views, forms, pagination)
│
├── reservas/                    # 📅 App de reservas e administração
│   ├── models.py                #    Modelo Reserva (cancelamento lógico)
│   ├── views.py                 #    14 views (dashboard, reservas, gestão de usuários)
│   ├── email_service.py         #    Notificações SMTP (confirmação + cancelamento)
│   ├── templates/reservas/      #    7 templates (dashboard, gestão, reservas)
│   └── tests/                   #    21+ testes de fluxo completo
│
├── scripts/                     # ⚙️ Utilitários e automações
│   ├── popular_banco_faker.py   #    Popula BD com dados realistas (Faker pt_BR)
│   ├── criar_salas_exemplo.py   #    Cria salas de exemplo
│   ├── criar_estudantes.py      #    Cria estudantes de teste
│   └── ...                      #    Scripts de manutenção e diagnóstico
│
├── ifteca_project/              # ⚙️ Configuração do projeto Django
│   ├── settings.py              #    Settings com variáveis de ambiente
│   └── urls.py                  #    Roteamento raiz
│
├── Dockerfile                   # 🐳 Imagem Python 3.12-slim
├── docker-compose.yml           # 🐳 Orquestração com volume SQLite
└── requirements.txt             # 📦 4 dependências diretas
```

---

## 🔧 Variáveis de Ambiente

Crie um arquivo `.env` na raiz para configuração (opcional):

```env
# Django
DJANGO_SECRET_KEY=sua-chave-secreta
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# E-mail (SMTP Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASS=sua-senha-de-app
RESERVA_EMAIL_DESTINO=destino@email.com
```

> Em ambiente de testes, o backend de e-mail é substituído automaticamente por `locmem` para evitar envios reais.

---

## 🗺️ Roadmap

- [ ] Trocar e-mail síncrono por fila assíncrona (Celery/RQ)
- [ ] Modo "somente leitura" para demonstração pública
- [ ] Suporte a múltiplos campi/andares
- [ ] Testes end-to-end com Playwright
- [ ] Migrar para PostgreSQL em produção
- [ ] Adicionar cobertura de código (coverage.py)

---

## 📄 Licença

Projeto acadêmico desenvolvido para a disciplina de **RAD (Rápido Desenvolvimento de Aplicações) — IFPB**.

---

<div align="center">

### Feito com ❤️ por

**[Danillo Coelho](https://github.com/Nillocoelho)** · **Pedro Henrique Barbosa** · **Cássia Dos Santos** · **Raiza Tomazoni**

⭐ Se este projeto foi útil, considere dar uma estrela no repositório!

[🔗 Ver no GitHub](https://github.com/Nillocoelho/IFteca_RAD)

</div>
