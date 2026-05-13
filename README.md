# LeadFlow CRM Workspace

A production-style, full-stack Lead Management CRM built as a **single workflow system** rather than a generic dashboard.

LeadFlow combines:
- a high-signal, low-friction React workspace UI,
- secure JWT authentication,
- async FastAPI services,
- and query/state patterns optimized for real sales execution speed.

---

## Screen Recording

> Add your app flow recording link here after uploading.

- `Demo Video:` **[PASTE LINK HERE]**
- `Optional Notes:` authentication flow, lead lifecycle, timeline updates, follow-up behavior

---

## Why This Stack Is Unique

This project is intentionally designed around a **multi-layer state architecture** and **async-first backend**, which is uncommon in basic CRUD assessments.

### 1) Three-State Frontend Architecture (Clear Separation of Concerns)
- **Server State**: `@tanstack/react-query` for fetching, caching, invalidation, optimistic UX patterns.
- **Client App State**: `zustand` for persistent UI/filter/auth/AI-local state.
- **Local Interaction State**: React component state for modal/form/control behavior.

This split avoids the common anti-pattern of overloading a single state system.

### 2) OAuth2-Compatible Login Flow with JWT
- Login uses `application/x-www-form-urlencoded` for FastAPI `OAuth2PasswordRequestForm` compatibility.
- JWT tokens are injected via axios request interceptors.
- Global `401` handling clears token and redirects to login.

### 3) Async Python Service Layer
- FastAPI + SQLAlchemy `asyncio` + `aiosqlite`.
- Route handlers stay thin; business logic is delegated to service modules.
- Strong schema contracts via Pydantic v2.

### 4) Workflow-Centric UX, Not Generic Admin UI
- Prioritized follow-ups (`follow_up_today`) and timeline logging.
- Status progression and discussion lifecycle are first-class.
- Auth and app flows are integrated, not bolted on.

---

## Monorepo Layout

```text
Esmagico-Assessment/
├── backend/
│   ├── app/
│   │   ├── core/            # config, DB session/engine
│   │   ├── models/          # SQLAlchemy models (User, Lead, Discussion)
│   │   ├── routes/          # FastAPI routers (auth, leads, discussions, users)
│   │   ├── schemas/         # Pydantic request/response models
│   │   └── services/        # business logic layer
│   ├── init_db.py           # database bootstrap (create/drop tables)
│   ├── requirements.txt
│   └── leadflow.db          # SQLite DB (local development)
│
├── frontend/
│   ├── src/
│   │   ├── components/      # UI modules + auth components
│   │   ├── hooks/           # React Query hooks + auth hooks
│   │   ├── lib/             # axios client, auth token helpers
│   │   ├── pages/           # routed auth pages
│   │   ├── store/           # Zustand stores
│   │   └── utils/           # date/time utility helpers
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
│
└── README.md
```

---

## System Architecture

### Frontend
- **Framework**: React 18 + Vite 7
- **Styling**: Tailwind CSS 3
- **Routing**: React Router v6 (`/login`, `/signup`, protected `/`)
- **Server State**: TanStack Query v5
- **Client State**: Zustand
- **HTTP**: Axios with auth interceptors and 401 handling
- **Motion/UI**: Framer Motion + Lucide icons

### Backend
- **Framework**: FastAPI
- **ASGI Server**: Uvicorn
- **ORM**: SQLAlchemy 2 (async)
- **DB Driver**: aiosqlite
- **Validation**: Pydantic v2
- **Auth**: JWT via `python-jose`, password hashing via `passlib[bcrypt]`

---

## Authentication & Authorization

### Public Routes
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me` (requires token)

### Protected App Behavior
- Frontend `ProtectedRoute` checks token presence.
- Axios request interceptor injects `Authorization: Bearer <token>`.
- Axios response interceptor handles `401` globally by clearing token and redirecting to `/login`.

### Login Contract (Important)
`/api/auth/login` expects URL-encoded payload:

```txt
Content-Type: application/x-www-form-urlencoded
username=<email>&password=<password>
```

---

## Core Domain Model

### User
- `id`, `name`, `email`, `password`, `created_at`

### Lead
- `id`, `name`, `company`, `phone`, `sales_rep_id`, `status`, `follow_up_at`, `created_at`, `updated_at`
- `status`: `New | Contacted | Qualified | Proposal Sent | Won | Lost`

### Discussion
- `id`, `lead_id`, `note`, `follow_up_at`, `created_at`
- Creating a discussion with `follow_up_at` propagates the follow-up value to the parent lead.

---

## API Surface (Implemented)

### Auth
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

### Leads
- `GET /api/leads`
  - Query params: `lead_id`, `status`, `search`, `company`, `phone`, `follow_up_today`
- `POST /api/leads`
- `PATCH /api/leads/{lead_id}`
- `DELETE /api/leads/{lead_id}`

### Discussions
- `GET /api/leads/{lead_id}/discussions`
- `POST /api/leads/{lead_id}/discussions`

### Users
- `GET /api/users`
- `GET /api/users/{user_id}`
- `PATCH /api/users/{user_id}`
- `DELETE /api/users/{user_id}`

---

## Local Development Setup

## Prerequisites
- Python `3.10+`
- Node.js `18+` (or newer LTS)
- npm

## 1) Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create/verify your `.env` in `backend/`:

```env
DATABASE_URL=sqlite+aiosqlite:///./leadflow.db
ENVIRONMENT=development
SECRET_KEY=your-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
UPSTASH_REDIS_REST_URL=...
UPSTASH_REDIS_REST_TOKEN=...
ANTHROPIC_API_KEY=...
```

Initialize DB (if needed):

```bash
python init_db.py
```

Run API server (port `8000`):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

## 2) Frontend Setup

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite runs on `http://localhost:5173`.

`vite.config.js` proxies `/api` to backend on `http://localhost:8000`.

---

## Runbook (Recommended Terminal Split)

Terminal A (Backend):
```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Terminal B (Frontend):
```bash
cd frontend
npm run dev
```

---

## Environment & Security Notes

- Do not commit real secrets to version control.
- Rotate any exposed API tokens or JWT secrets before production use.
- Use environment-specific configs for staging/production.
- Restrict CORS origins in production (backend currently allows `*` for development convenience).

---

## UX & Product Capabilities

- Signup and login with JWT auth
- Protected workspace route
- Lead creation and status progression
- Discussion timeline per lead
- Follow-up scheduling and today filtering
- Search and status filters
- Profile menu with logout and auth cache reset

---

## Troubleshooting

### `Vite proxy ECONNREFUSED /api/...`
Cause: backend is not running on `localhost:8000`.

Fix:
1. Start FastAPI (`uvicorn app.main:app --reload --port 8000`).
2. Keep frontend on `5173`.
3. Verify `vite.config.js` proxy points to `http://localhost:8000`.

### `Failed to resolve import react-router-dom`
Cause: dependency not installed.

Fix:
```bash
cd frontend
npm install react-router-dom
```

### Login fails despite correct credentials
- Ensure frontend sends URL-encoded payload to `/api/auth/login`.
- Confirm request body keys are `username` and `password`.

---

## Suggested Next Enhancements

- Add migration tooling (Alembic) instead of table reset scripts.
- Add test suites:
  - Backend: `pytest` + async API tests.
  - Frontend: `vitest` + component/integration tests.
- Add RBAC/ownership checks for lead update/delete paths.
- Add observability (structured logs + request tracing).
- Add Dockerized dev/prod environments.

---

## License

Add your preferred license here (MIT, Apache-2.0, proprietary, etc.).
