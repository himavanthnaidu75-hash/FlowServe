# FlowServe — Backend

FastAPI backend for **FlowServe**, the all-in-one service delivery platform for digital freelancers and agencies.

## Stack

- **FastAPI** — async API framework
- **SQLAlchemy 2.0** — async ORM
- **asyncpg** — Postgres driver
- **Pydantic v2** — schemas + settings
- **python-jose** — JWT auth
- **passlib[bcrypt]** — password hashing
- **Stripe / SendGrid** — payments + email (stubs included for dev)

## Quickstart

### Prerequisites
- Python 3.11+
- PostgreSQL running locally (or use docker)

### Install
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```

### Configure
```bash
copy .env.example .env
# Edit .env: set DATABASE_URL and JWT_SECRET
```

Generate a strong JWT secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### Initialize DB (auto-create tables)
The dev server will run `Base.metadata.create_all()` on startup. For production use [Alembic](#migrations).
Make sure your Postgres DB exists first:
```bash
# Log into psql and:
CREATE DATABASE flowserve;
```

### Run
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
The API will be at `http://localhost:8000/api` and the (auto-generated) OpenAPI docs at `http://localhost:8000/docs`.

## API contract (matches frontend)

| Method      | Endpoint                     | Purpose                                |
| ----------- | ---------------------------- | -------------------------------------- |
| POST        | `/api/auth/signup`           | Create account                         |
| POST        | `/api/auth/login`            | Get JWT                                |
| GET         | `/api/auth/me`               | Current user                           |
| GET         | `/api/dashboard/stats`       | Top KPI numbers                        |
| GET         | `/api/dashboard/revenue`     | Monthly revenue series                 |
| GET/POST    | `/api/projects`              | List / create project                  |
| GET/PATCH   | `/api/projects/{id}`         | Get / update project                   |
| DELETE      | `/api/projects/{id}`         | Delete project                         |
| PATCH       | `/api/projects/{id}/status`  | Change status only                     |
| GET/POST    | `/api/clients`                | List / create client                   |
| GET/PATCH   | `/api/clients/{id}`          | Get / update client                    |
| GET/POST    | `/api/proposals`              | List / create proposal                 |
| GET/PATCH   | `/api/proposals/{id}`         | Get / update proposal                  |
| POST        | `/api/proposals/{id}/send`    | Send proposal to client                |
| GET/POST    | `/api/invoices`               | List / create invoice                  |
| GET/PATCH   | `/api/invoices/{id}`          | Get / update invoice                   |
| POST        | `/api/invoices/{id}/pay`      | Mark invoice paid                      |
| POST        | `/api/invoices/{id}/remind`   | Send payment reminder                  |
| GET/POST    | `/api/time-entries`           | List / create time entry               |
| PATCH       | `/api/time-entries/{id}`      | Update time entry                      |
| GET/PATCH   | `/api/settings`               | Get / update user settings             |
| GET         | `/api/portal/{token}`         | Public client portal (token auth)      |

All `/api/*` routes except `/api/auth/*` and `/api/portal/*` require a `Authorization: Bearer <jwt>` header.

## Migrations (production)
```bash
alembic init alembic
# point sqlalchemy.url to DATABASE_URL in alembic.ini
alembic revision --autogenerate -m "init schema"
alembic upgrade head
```

## Dev Notes
- Stripe / SendGrid calls are wrapped in stubs in `app/core/integrations.py`. They print to the console instead of making real API requests when no key is set.
- A seed script (`scripts/seed.py`) is included to populate some sample data for local development.
