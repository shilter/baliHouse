# BaliHouses Lead Tracker

A mini lead management app — Flask (Python) backend + Vite/React frontend.

## Stack

| Layer    | Tech                                           |
|----------|------------------------------------------------|
| Backend  | Flask 2.1, Flask-RESTful, Flask-JWT-Extended, SQLAlchemy, Flask-Migrate |
| Database | PostgreSQL                                     |
| Frontend | React 18 + Vite                                |
| Auth     | x-api-key (leads) + JWT Bearer (members)       |

---

## Project Structure

```
baliHouse/
├── backend/
│   ├── app/
│   │   ├── middleware/       # require_api_key re-export
│   │   ├── models/           # LeadsModel, MemberModel, TokensBlocklistModels
│   │   ├── resources/
│   │   │   ├── leads/        # CRUD endpoints
│   │   │   └── members/
│   │   │       ├── auth.py   # register, login, logout, me, refresh
│   │   │       └── membersResources.py  # member CRUD + pagination
│   │   ├── security/
│   │   │   └── utils.py      # require_api_key + JWT setup + blocklist
│   │   ├── .env
│   │   └── requirements.txt
│   └── migrations/
├── frontend/
│   ├── src/
│   │   ├── api.js            # apiFetch (x-api-key) + authFetch (JWT)
│   │   ├── App.jsx           # auth state + page routing
│   │   ├── LoginPage.jsx
│   │   ├── RegisterPage.jsx
│   │   └── LeadsPage.jsx     # leads CRUD UI
│   └── .env
└── venv/
```

---

## Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL 15+

---

## 1. PostgreSQL Setup

```bash
# Create user and database
sudo -u postgres psql <<'SQL'
CREATE USER leadstasksuser WITH PASSWORD 'your_password';
CREATE DATABASE leadstasks OWNER leadstasksuser;
GRANT ALL PRIVILEGES ON DATABASE leadstasks TO leadstasksuser;
SQL

# Grant schema access (required for PostgreSQL 15+)
sudo -u postgres psql -d leadstasks <<'SQL'
GRANT ALL ON SCHEMA public TO leadstasksuser;
ALTER SCHEMA public OWNER TO leadstasksuser;
SQL
```

---

## 2. Backend Setup

```bash
# From the project root
cd backend

# Create and activate virtualenv (if not already created)
python -m venv ../venv
source ../venv/bin/activate        # Windows: ..\venv\Scripts\activate

# Install dependencies
pip install -r app/requirements.txt

# Configure environment
cp app/.env.example app/.env
# Edit app/.env — set username, password, database, secret, api_key
```

### Environment Variables (`backend/app/.env`)

| Variable    | Description                              | Example                  |
|-------------|------------------------------------------|--------------------------|
| `username`  | PostgreSQL username                      | `leadstasksuser`         |
| `password`  | PostgreSQL password                      | `yourpassword`           |
| `dsn`       | Database host                            | `127.0.0.1`              |
| `database`  | Database name                            | `leadstasks`             |
| `port`      | Database port                            | `5432`                   |
| `connection`| DB driver                                | `postgresql`             |
| `secret`    | JWT secret key (any long random string)  | `abc123...`              |
| `algorithm` | JWT algorithm                            | `HS256`                  |
| `api_key`   | x-api-key value for leads endpoints      | `abc123...`              |
| `page`      | Default page number                      | `1`                      |
| `per_page`  | Default items per page                   | `10`                     |

---

## 3. Database Migration

Run all commands from the `backend/` directory with the virtualenv active.

```bash
cd backend
source ../venv/bin/activate
export FLASK_ENV=development
export FLASK_APP=app.run

# First time only — create the migrations folder
flask db init

# Generate migration file from models
flask db migrate -m "initial schema"

# Apply migration to the database
flask db upgrade
```

### Migration reference

| Command                          | When to run                          |
|----------------------------------|--------------------------------------|
| `flask db init`                  | Once — initialises migrations folder |
| `flask db migrate -m "message"`  | After adding or changing a model     |
| `flask db upgrade`               | Apply pending migrations to DB       |
| `flask db downgrade`             | Roll back one migration              |
| `flask db history`               | Show migration history               |

---

## 4. Run the Backend

```bash
cd backend
source ../venv/bin/activate
FLASK_ENV=development python app/run.py
# Server → http://localhost:5000
```

---

## 5. Frontend Setup

```bash
cd frontend
npm install
npm run dev
# App → http://localhost:3000
```

### Environment Variables (`frontend/.env`)

| Variable           | Description                        |
|--------------------|------------------------------------|
| `VITE_API_BASE_URL`| Backend URL (proxied in dev)       |

> The `api_key` is **not** stored in the frontend `.env`. It is returned by the backend
> on login (`POST /api/members/login`) and saved to `localStorage` automatically.

---

## API Endpoints

### Health

| Method | Path         | Auth     | Description  |
|--------|--------------|----------|--------------|
| GET    | /api/health  | none     | Server check |

### Leads (all require `x-api-key` header)

| Method | Path              | Description                            |
|--------|-------------------|----------------------------------------|
| GET    | /api/leads        | List all leads. Supports `?status=`    |
| POST   | /api/leads        | Create a lead                          |
| PATCH  | /api/leads/:id    | Update status and/or notes             |
| DELETE | /api/leads/:id    | Delete a lead                          |

### Members — Auth (no auth required)

| Method | Path                   | Description                             |
|--------|------------------------|-----------------------------------------|
| POST   | /api/members/register  | Create account                          |
| POST   | /api/members/login     | Login — returns JWT + api_key           |

### Members — Auth (JWT Bearer required)

| Method | Path                   | Description                             |
|--------|------------------------|-----------------------------------------|
| DELETE | /api/members/logout    | Logout — revokes token to blocklist     |
| GET    | /api/members/me        | Current member profile                  |
| POST   | /api/members/refresh   | Get new access token from refresh token |

### Members — CRUD (JWT Bearer required)

| Method | Path                   | Description                             |
|--------|------------------------|-----------------------------------------|
| GET    | /api/members           | List members. Supports `?q=&page=&per_page=` |
| GET    | /api/members/:id       | Get one member                          |
| PATCH  | /api/members/:id       | Update name / email / password (own only) |
| DELETE | /api/members/:id       | Delete account (own only)               |

---

## Example curl Commands

### Register & Login

```bash
# Register
curl -X POST http://localhost:5000/api/members/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Doe","email":"jane@example.com","password":"secret123"}'

# Login — response includes access_token, refresh_token, api_key
curl -X POST http://localhost:5000/api/members/login \
  -H "Content-Type: application/json" \
  -d '{"email":"jane@example.com","password":"secret123"}'
```

### Leads (use api_key from login response)

```bash
export API_KEY="<api_key from login response>"

# List all leads
curl http://localhost:5000/api/leads \
  -H "x-api-key: $API_KEY"

# Filter by status
curl "http://localhost:5000/api/leads?status=new" \
  -H "x-api-key: $API_KEY"

# Create a lead
curl -X POST http://localhost:5000/api/leads \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"John Smith","email":"john@example.com","budget":250000,"phone":"+62 812 0000"}'

# Update status
curl -X PATCH http://localhost:5000/api/leads/<id> \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status":"qualified"}'

# Delete
curl -X DELETE http://localhost:5000/api/leads/<id> \
  -H "x-api-key: $API_KEY"
```

### Member endpoints (use access_token from login response)

```bash
export TOKEN="<access_token from login response>"

# Get current profile
curl http://localhost:5000/api/members/me \
  -H "Authorization: Bearer $TOKEN"

# List members with search + pagination
curl "http://localhost:5000/api/members?q=jane&page=1&per_page=10" \
  -H "Authorization: Bearer $TOKEN"

# Logout (revokes token)
curl -X DELETE http://localhost:5000/api/members/logout \
  -H "Authorization: Bearer $TOKEN"
```

---

## Known Limitations

- Leads list has no pagination — all matching rows are returned in one response.
- Redis is optional — token blocklist falls back to PostgreSQL if `REDIS_URL` is not set.
- No rate limiting on API endpoints.
- Members can only update/delete their own account (no admin role yet).