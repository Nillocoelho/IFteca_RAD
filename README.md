# IFTECA – Sistema de Reserva de Salas

Projeto acadêmico em Django que entrega autenticação, gestão de salas, criação/cancelamento de reservas e um painel administrativo completo com gráficos e exportação em PDF. Pensado para ser mostrado em feira ou banca: fácil de subir, com dados fictícios e suite de testes cobrindo os fluxos principais.

## Visão Geral

- **Público-alvo:** bibliotecas, laboratórios e salas de estudo em instituições de ensino.
- **Perfis:**  
  - **Administrador/Staff:** gerencia salas, usuários e reservas; emite relatórios.  
  - **Professor/Estudante:** consulta salas, cria e cancela as próprias reservas.
- **API + UI:** endpoints REST (DRF) e front-end server-side com Bootstrap 5.

## Principais Funcionalidades

- Login com sessão e token (DRF), proteção CSRF e timeout de sessão.
- CRUD de salas com soft delete, status (Disponivel / Em Manutencao) e equipamentos.
- Reserva de horários sem sobreposição, cancelamento pelo usuário e pelo admin.
- Dashboard com KPIs, gráficos (Chart.js) e exportação de relatório em PDF (jsPDF).
- Paginação em listas de salas, reservas e usuários (8 itens/página).
- Scripts Faker para popular rapidamente com dados de exemplo.

## Arquitetura (apps)

- `auth_app` – login/logout, serializers e endpoints de autenticação.
- `salas` – modelos e views de salas, páginas públicas de listagem.
- `reservas` – lógica de reserva, dashboard, APIs administrativas.
- `ifteca_project` – settings, URLs, WSGI/ASGI.

## Stack e Dependências

- Python 3.11+ / Django 5.1
- Django REST Framework, Authtoken
- SQLite para dev (default), pronto para outro backend via `DATABASES`
- Bootstrap 5, Chart.js, jsPDF
- Faker (dados fictícios), django-ratelimit, livereload (dev)

## Como Rodar (local)

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Como Rodar (Docker)

```bash
docker compose build
docker compose up -d
docker compose exec web python manage.py migrate
```

Aplicação: http://localhost:8000

## Dados de Exemplo (Faker)

Popular o banco com salas/usuários/reservas sintéticos (professores NÃO recebem permissões de admin e admins não ganham reservas):

```bash
python manage.py shell -c "exec(open('scripts/popular_banco_faker.py', 'r', encoding='utf-8').read())"
```

## Perfis e Regras

- **Administrador (is_superuser=True):** tudo; cancela qualquer reserva; acessa “Gerenciar Usuários”.
- **Staff (is_staff=True, não superuser):** pode gerenciar reservas e salas; não cancela reservas de outros admins; vê “Gerenciar Usuários”.
- **Professor/Estudante (is_staff=False):** faz/cancela apenas as próprias reservas; não acessa páginas de gestão.
- Admin/Staff são bloqueados no endpoint de criação de reserva (não fazem reservas).

## Segurança e Sessão

- CSRF habilitado em POST/PUT/DELETE via fetch com `X-CSRFToken`.
- Sessão expira ao fechar o navegador e por tempo (`SESSION_COOKIE_AGE=1800`), renovada a cada requisição.
- Ratelimit no login (django-ratelimit).

## APIs Principais (caminhos úteis)

- Reservas públicas: `GET /reservas/salas/publicas/`
- Horários disponíveis: `GET /api/salas/<id>/horarios/?data=YYYY-MM-DD`
- Criar reserva (estudante): `POST /api/reservas/criar/`
- Cancelar reserva (estudante): `POST /api/reservas/<id>/cancelar/`
- Dashboard data (admin): `GET /reservas/api/dashboard/`
- Gestão de salas (admin): `POST/PUT/DELETE /reservas/admin/salas/...` e `/salas/api/salas/…`

## Testes

```bash
python manage.py test
```

Cobrem models, views, APIs, paginação e fluxo de reservas (169 testes).

## Scripts Úteis

- `scripts/popular_banco_faker.py` – popula dados.
- `scripts/corrigir_equipamentos.py` – exemplo de manutenção de dados.

## Estrutura

- `auth_app/` – autenticação e static/login.
- `salas/` – modelos, templates e JS de salas.
- `reservas/` – dashboard, reservas, templates e JS (PDF, toasts, etc.).
- `scripts/` – automações de dados.
- `data/db.sqlite3` – banco local (não versionado).

## Roadmap Sugerido (acadêmico)

- Trocar e-mail síncrono por fila (Celery/RQ) para UX mais rápida.
- Modo “somente leitura” para demonstração pública.
- Permitir múltiplos calendários (campus/andar) e anexos em salas.
- Adicionar testes end-to-end (Playwright).

---

Equipe: Danillo Coelho Barbosa, Pedro Henrique Barbosa, Cássia Dos Santos, Raiza Tomazoni

Feito para apresentação acadêmica: suba, popular com Faker, navegue no dashboard, exporte o PDF e mostre as telas de estudante versus admin para evidenciar os controles de acesso.
