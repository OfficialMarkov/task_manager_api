# Task Manager API

Production-ready REST API for managing personal tasks, built with FastAPI, async SQLAlchemy, JWT auth and full test coverage.  
Designed as a compact, real-world backend service suitable for junior/internship portfolios.

---

## Features

- User registration and login with JWT authentication.
- Role-based access control (`user`, `admin`).
- CRUD for tasks (create/read/update/delete).
- Pagination, filtering by completion status and text search.
- Protection so users can only access their own tasks; admins can access all.
- Centralized error handling and validation.
- Async database access and fully async tests.

---

## Tech Stack

- **Language & Framework**
  - Python 3.10+
  - FastAPI

- **Data & Persistence**
  - SQLite (default for local/dev)
  - PostgreSQL (via Docker Compose)
  - SQLAlchemy 2.x (async)
  - Alembic (migrations)

- **Auth & Security**
  - JWT (python-jose)
  - Password hashing with Passlib (`pbkdf2_sha256`)

- **Testing**
  - pytest
  - pytest-asyncio
  - httpx (AsyncClient + ASGITransport)

- **Tooling**
  - Docker, docker-compose
  - pydantic / pydantic-settings

---

## Project Structure

```text
task_manager_api/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py          # Auth endpoints (register, login, /me)
│   │   │   └── tasks.py         # Task CRUD and listing
│   │   └── deps.py              # Shared dependencies (DB session, JWT, roles)
│   ├── core/
│   │   ├── config.py            # Settings (env variables, defaults)
│   │   └── security.py          # Password hashing and JWT helpers
│   ├── db/
│   │   ├── models.py            # SQLAlchemy ORM models (User, Task)
│   │   ├── session.py           # Async DB engine and session factory
│   │   └── base.py              # Base metadata (for Alembic)
│   ├── schemas/
│   │   ├── auth.py              # Auth-related Pydantic schemas
│   │   └── task.py              # Task-related Pydantic schemas
│   ├── services/
│   │   └── task_service.py      # Business logic for tasks
│   └── main.py                  # FastAPI app factory and error handlers
├── alembic/                     # Database migrations
├── tests/
│   ├── conftest.py              # Async fixtures, test DB, test client
│   ├── test_auth.py             # Auth tests
│   └── test_tasks.py            # Task tests
├── docker-compose.yml
├── Dockerfile
├── env.example                  # Example environment variables
└── pyproject.toml / requirements.txt
```

Architecture principles:

- Clear separation of concerns: routes / services / models / schemas / core.
- Dependency injection via `Depends` for DB and auth.
- Fully async DB access using SQLAlchemy async engine and sessions.

---

## Database Model

### `users`

| Field          | Type                | Description              |
|----------------|---------------------|--------------------------|
| id             | Integer (PK)        | User ID                  |
| email          | String (UNIQUE)     | User email               |
| hashed_password| String              | Password hash            |
| is_active      | Boolean             | Is user active           |
| role           | Enum(`user`,`admin`)| User role                |
| created_at     | DateTime            | Created at               |
| updated_at     | DateTime            | Updated at               |

### `tasks`

| Field      | Type           | Description                     |
|------------|----------------|---------------------------------|
| id         | Integer (PK)   | Task ID                         |
| title      | String         | Task title                      |
| description| String         | Task description (optional)     |
| completed  | Boolean        | Completion status               |
| owner_id   | Integer (FK)   | FK to `users.id`                |
| created_at | DateTime       | Created at                      |
| updated_at | DateTime       | Updated at                      |

Relations:

- `users` 1:N `tasks` (one user has many tasks).
- Cascade delete on user → tasks.

---

## API Overview

Base prefix: `/api/v1`

### Auth (`/api/v1/auth`)

- `POST /register` — create a new user.
- `POST /login` — obtain JWT access token.
- `GET /me` — get current user profile.

### Tasks (`/api/v1/tasks`)

- `POST /tasks` — create task (auth required).
- `GET /tasks` — list tasks with pagination and filters.
  - `page` — page number (default `1`).
  - `page_size` — page size (default `10`, max `100`).
  - `completed` — filter by status (`true` / `false`).
  - `search` — search in title and description.
- `GET /tasks/{id}` — get task by id (owner or admin).
- `PUT /tasks/{id}` — partial update of task.
- `DELETE /tasks/{id}` — delete task.

Error codes:

- `400` — bad request.
- `401` — unauthorized.
- `403` — forbidden.
- `404` — not found.
- `422` — validation error.
- `500` — internal server error.

Interactive docs (after start):

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Quickstart (local, SQLite, no Docker)

This mode is ideal for reviewers and for running tests quickly.

1. Create and activate virtualenv (example for Windows PowerShell):

```bash
python -m venv venv
.\venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

3. (Optional) Create `.env` from `env.example` and adjust values.  
   By default, the app uses a local SQLite DB: `sqlite+aiosqlite:///./task_manager.db`.

4. Run the app:

```bash
uvicorn app.main:app --reload
```

5. Open `http://localhost:8000/docs` to try the API.

---

## Running with Docker & PostgreSQL

1. Clone the repository:

```bash
git clone <repository-url>
cd task_manager_api
```

2. Create `.env` from `env.example` in the project root and set at least:

- `SECRET_KEY` — strong random string (≥ 32 chars).
- `DATABASE_URL` — PostgreSQL URL (Docker default is usually fine).

3. Start services:

```bash
docker-compose up -d
```

4. Apply migrations:

```bash
docker-compose exec api alembic upgrade head
```

5. Open `http://localhost:8000/docs`.

---

## Tests

Run tests locally (from project root, with venv activated):

```bash
python -m pytest
```

All tests are async and use a separate SQLite test database.  
They cover:

- Registration and login.
- Access token flow and `/auth/me`.
- Task CRUD operations.
- Pagination, filtering and search.
- Access control (users cannot read other users’ tasks).

---

## Environment Variables

Create a `.env` file in the project root (next to `env.example`).

Key variables:

- `DATABASE_URL` — DB connection string.
- `SECRET_KEY` — JWT signing key (must be overridden in production).
- `ACCESS_TOKEN_EXPIRE_MINUTES` — token lifetime (default 30).
- `API_V1_PREFIX` — API prefix (default `/api/v1`).

To generate a secure `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Why this project is relevant for internships

- Uses a realistic backend stack: FastAPI, async SQLAlchemy, JWT, Alembic, Docker.
- Clean separation of layers (routes/services/db/schemas/core).
- Fully async code and tests, including proper async fixtures.
- Complete test suite (16 tests) that can be run with a single command.
- Easy to clone, run and review thanks to SQLite quickstart and clear structure.

You can mention this project in your CV as:

> “Task Manager API — production-style FastAPI backend with JWT auth, async SQLAlchemy, alembic migrations and full pytest coverage.”

And link directly to this repository and to the `/docs` endpoint on a live deployment (if you deploy it).

---

## Кратко по‑русски

Task Manager API — это учебный, но достаточно боевой backend-сервис для управления задачами:

- FastAPI, async SQLAlchemy, JWT, Alembic, Docker.
- Регистрация, логин, роли пользователей, доступ только к своим задачам.
- Пагинация, фильтрация, поиск.
- Полный набор асинхронных тестов на pytest.

Проект хорошо подходит как демонстрация навыков для стажировки или позиции junior backend‑разработчика.

---

## License

MIT
