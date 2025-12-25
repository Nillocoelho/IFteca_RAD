# IFteca_RAD

Um sistema leve de gerenciamento e reserva de salas desenvolvido em Django, pensado para uso acadêmico e institucional — autenticação, cadastro e gerenciamento de salas, criação e visualização de reservas, e uma interface administrativa pronta para uso.

Principais componentes:

- `auth_app`: autenticação e views de login.
- `salas`: modelos e views para gerenciar salas (capacidade, localização, equipamentos).
- `reservas`: criação e gerenciamento de reservas, confirmação e cancelamento.
- `ifteca_project`: configuração do projeto Django (settings, URLs, WSGI/ASGI).

Características
---------------

- Autenticação de usuários com telas de login.
- CRUD completo para salas e reservas.
- Templates responsivos com JS/CSS para interação no frontend.
- Suporte a execução via Docker (arquivo `docker-compose.yml`).
- Conjunto de testes unitários para modelos, views e APIs.

Tecnologias
----------

- Python 3.x
- Django
- SQLite (padrão para desenvolvimento)
- Docker + Docker Compose (opcional para deploy/ambiente)

Instalação Rápida (ambiente local)
---------------------------------

1. Clone o repositório:

```bash
git clone https://github.com/Nillocoelho/IFteca_RAD.git
cd IFteca_RAD
```

2. Crie e ative um ambiente virtual (Windows):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Instale dependências:

```bash
pip install -r requirements.txt
```

4. Aplique migrações e crie um superusuário:

```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Execute o servidor de desenvolvimento:

```bash
python manage.py runserver
```

Execução com Docker
-------------------

Se preferir usar Docker (recomendado para replicar ambiente):

```bash
docker compose build
docker compose up -d
docker compose exec web python manage.py migrate
```

Testes
------

Execute a suíte de testes com:

```bash
python manage.py test
```

Estrutura do Projeto (resumo)
----------------------------

- `auth_app/` — autenticação, serializers e templates de login
- `salas/` — modelos, views, templates e testes relacionados às salas
- `reservas/` — lógica de reserva, confirmações e templates
- `ifteca_project/` — configuração Django e rotas do projeto
- `scripts/` — scripts auxiliares para popular dados de exemplo
- `data/` — backups e arquivos de dados locais

Contribuindo
------------

- Abra uma issue para discutir mudanças ou melhorias.
- Envie pull requests com pequenas alterações e descrições claras.
- Mantenha estilo de código consistente e inclua testes quando apropriado.

Licença
-------

Este repositório está pronto para receber uma licença — sugiro MIT. Adicione um arquivo `LICENSE` se desejar publicar sob termos específicos.

Contato
-------

Criado por Nillocoelho — abra uma issue ou PR no GitHub para sugestões e dúvidas.

---

Bom trabalho! Se quiser, posso também:

- adicionar badges (build, cobertura, license);
- criar um `docker-compose.override.yml` de exemplo;
- gerar um arquivo `CONTRIBUTING.md` com orientações mais detalhadas.
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

Rodar com Docker:
1. Copie o exemplo de env: `cp .env.example .env` e ajuste `DJANGO_SECRET_KEY`/hosts se quiser.
2. Build: `docker compose build`
3. Subir: `docker compose up`
   - App em http://localhost:8000
   - LiveReload (se usar) expõe 35729
   - Banco SQLite persiste no volume `sqlite_data` (montado em `/app/data`)
4. Rodar comandos Django dentro do container: `docker compose run --rm web python manage.py migrate`
