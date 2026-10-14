# API de Cirurgias

REST API for managing a hospital's surgery schedule: surgeries, the professionals who make up each surgical team, and JWT-based access control. Built with FastAPI and PostgreSQL.

## Stack

- **FastAPI** — HTTP layer, validation (Pydantic v2), OpenAPI docs
- **SQLAlchemy 2** — ORM
- **PostgreSQL** — database (`psycopg2`)
- **JWT** — OAuth2 password flow, HS256 tokens (`python-jose`), bcrypt password hashing (`passlib`)
- **Docker** — container image based on `python:3.11.9-slim-bullseye`
- **Gunicorn** — production server, 4 Uvicorn workers

## Endpoints

All routes except `/token` require an `Authorization: Bearer <token>` header.

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/token` | Log in with username and password (form data), returns a JWT valid for 30 minutes |
| `GET` | `/api/v1/cirurgias/` | List surgeries. Query params: `data` (YYYY-MM-DD), `medico_nome` (partial match), `skip`, `limit` |
| `POST` | `/api/v1/profissionais/` | Create a professional |
| `GET` | `/api/v1/profissionais/` | List professionals |
| `GET` | `/api/v1/profissionais/{profissional_id}` | Get a professional by ID |
| `PUT` | `/api/v1/profissionais/{profissional_id}` | Update a professional |
| `DELETE` | `/api/v1/profissionais/{profissional_id}` | Delete a professional |

Interactive docs are served at `/docs` (Swagger UI) and `/redoc`.

## Running locally

Requires Python 3.11+ and a running PostgreSQL instance.

### 1. Clone

```bash
git clone https://github.com/YagoCalomino/api-cirurgias-fastapi.git
cd api-cirurgias-fastapi
```

### 2. Configure the environment

Create the database:

```bash
createdb -U postgres cirurgias_db
```

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost/cirurgias_db
SECRET_KEY=change-me
```

Tables are created automatically on startup.

### 3. Start the API

**With Uvicorn:**

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`.

**With Docker:**

```bash
docker build -t api-cirurgias .
docker run --env-file .env -p 10000:10000 api-cirurgias
```

The API is available at `http://localhost:10000`. Inside the container `localhost` is the container itself, so point `DATABASE_URL` at a host the container can reach (for example `host.docker.internal` on Docker Desktop).

### 4. Create a user

There is no sign-up endpoint. Generate a bcrypt hash and insert the user directly:

```bash
python hash_password.py   # edit the password in the script first
```

```sql
INSERT INTO usuarios (username, hashed_password) VALUES ('admin', '<generated hash>');
```

## Example request

Get a token:

```bash
curl -X POST http://localhost:8000/token \
  -d "username=admin" \
  -d "password=minhasenha123"
```

```json
{ "access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer" }
```

Create a professional:

```bash
curl -X POST http://localhost:8000/api/v1/profissionais/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"nome": "Dra. Ana Souza", "conselho_profissional": "CRM/SP 123456"}'
```

```json
{ "nome": "Dra. Ana Souza", "conselho_profissional": "CRM/SP 123456", "id": 1 }
```

List surgeries for a given day and surgeon:

```bash
curl "http://localhost:8000/api/v1/cirurgias/?data=2025-10-10&medico_nome=silva" \
  -H "Authorization: Bearer <access_token>"
```

## Project structure

```
.
├── app/
│   ├── main.py          # FastAPI app, CORS, routes
│   ├── database.py      # Engine, session factory, get_db dependency
│   ├── models.py        # SQLAlchemy models: usuarios, profissionais, cirurgias, equipe_cirurgica
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── security.py      # Password hashing, JWT creation and validation
│   └── tests/
│       └── test_main.py # Pytest suite
├── hash_password.py     # Helper script to generate a bcrypt hash
├── Dockerfile
├── pyproject.toml       # Pytest configuration
└── requirements.txt
```

## Tests

```bash
pytest
```

The suite runs against a separate PostgreSQL database, `cirurgias_db_test`, on `localhost`. `test_fluxo_completo_cirurgia` covers surgery create and read-by-ID routes that are not implemented yet, so it currently fails.
