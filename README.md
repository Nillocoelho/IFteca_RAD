IFteca_RAD

Projeto Django consolidado (Django 5).

Estrutura atual:
- `manage.py` — entrypoint apontando para `ifteca_project.settings`.
- `ifteca_project/` — configurações do projeto (settings/urls/wsgi).
- `salas/` — app de gerenciamento de salas (templates em `salas/templates/salas`, estáticos em `salas/static/salas`).
- `reservas/` — app de reservas (rotas sob `/reservas/...`).
- `auth_app/` — autenticação/REST.
- `data/db.sqlite3` — banco local (não versionado).
- `legacy_IFTECA_backup/` — backup do projeto antigo (somente consulta).

Como rodar:
1. Ativar venv: `.\venv\Scripts\Activate` (ou `.\.venv\Scripts\Activate`)
2. `python manage.py migrate`
3. `python manage.py runserver`
