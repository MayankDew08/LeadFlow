# ⚡ LeadFlow

A production-style Lead Management CRM built for sales reps — single screen, modal-driven, AI-augmented.

> Built as a take-home assessment for the Es Magico Fullstack Intern role.

---

## 🎬 Demo

📹 **Walkthrough Video**: <a href="[https://drive.google.com/file/d/1T-aRgZDUKcdGSpfexXrlcPj4mhEHEJnL/view?usp=sharing](https://drive.google.com/file/d/1T-aRgZDUKcdGSpfexXrlcPj4mhEHEJnL/view?usp=sharing)">Watch on Google Drive</a>

---

## ✨ Features

### Core CRM
- 🔐 JWT authentication (signup, login, protected routes)
- 📋 Single-screen lead list with status filters and name search
- 📌 Today's follow-ups pinned at the top
- 🔴 Overdue follow-ups highlighted in red
- 💬 Lead timeline dialog with full discussion history
- ✍️ Add discussions with optional follow-up datetime — propagates to lead instantly
- ➕ Add new lead (name required, company/phone optional)
- 🔄 Status updates from within the dialog
- ⚡ Optimistic UI updates for instant perceived performance

### AI-Powered Workflows
1. **Company Enrichment** — Web-grounded company intelligence on lead creation (industry, size, HQ, website, recent news, sales angles)
2. **Lead Summarization** — Instant AI brief from discussion history
3. **Lead Scoring** — Hot / Warm / Cold classification with reasoning and recommended action
4. **Follow-up Suggestion** — Extracts implied timing from natural language notes
5. **Email Generation** — Personalized sales emails with purpose + tone control, copy/mailto integration

### Production Engineering
- 🛡 **Multi-provider AI fallback chains** (Groq → Gemini → graceful degradation)
- ⚡ **Redis caching** (Upstash) with smart invalidation
- 🐳 **Docker Compose** for one-command setup
- 🌐 **Nginx reverse proxy** (eliminates CORS, proxies `/api` to backend)
- 📝 **Structured logging** across all layers
- 🛑 **Graceful error handling** — AI failures never block core CRM actions
- 🧪 **12 passing tests** (smoke + integration)

---

## 🚀 Quick Start

### Prerequisites
- Docker + Docker Compose
- A Supabase account (free) — for PostgreSQL
- An Upstash account (free) — for Redis
- Free API keys: <a href="https://console.groq.com">Groq</a>, <a href="https://aistudio.google.com">Gemini</a>, <a href="https://tavily.com">Tavily</a>

### One-Command Setup

```bash
# 1. Clone
git clone https://github.com/MayankDew08/LeadFlow
cd LeadFlow

# 2. Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your credentials

cp frontend/.env.example frontend/.env

# 3. Start everything
docker compose up --build

# 4. Seed the database (in another terminal)
docker compose exec backend python seed.py
```

### Access

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

### Test Credentials

```text
Email:    test@leadflow.dev
Password: test1234
```

---

## 🧪 Testing

The backend ships with **12 tests** covering smoke checks and critical integration flows.

```bash
# Run all tests inside the container
docker compose exec backend pytest -v

# With coverage
docker compose exec backend pytest --cov=app

# Run a specific test file
docker compose exec backend pytest tests/test_leads.py -v
```

**Test Coverage**
- ✅ Authentication flows (register, login, protected routes)
- ✅ Lead CRUD with status filtering and search
- ✅ Discussion creation with follow-up propagation
- ✅ Health check + database connectivity
- ✅ Error states (404s, 422s, 401s)

---

## 🏗 Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   Browser                                                    │
│      │                                                       │
│      ▼                                                       │
│  ┌────────────────┐                                          │
│  │  Nginx (Port 3000)                                       │
│  │  Serves React  │ ─── /api/* ───┐                          │
│  └────────────────┘                ▼                         │
│                              ┌──────────────┐                │
│                              │ FastAPI :8000│                │
│                              └──────┬───────┘                │
│                                     │                        │
│              ┌──────────────────────┼───────┐                │
│              ▼                              ▼                │
│        ┌──────────┐                    ┌──────────┐
│        │ Supabase │                    │ AI APIs  │
│        │ Postgres │                    │ Groq +   │
│        │          │                    │ Gemini + │
│        │          │                    │ Tavily   │
│        └──────────┘                    └──────────┘
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🛠 Tech Stack

### Backend
- FastAPI (Python 3.11)
- SQLAlchemy + Pydantic v2
- PostgreSQL (Supabase) with connection pooling
- Redis (Upstash) for caching
- JWT auth via OAuth2PasswordBearer
- Pytest for testing

### Frontend
- React 18 + Vite
- TailwindCSS + shadcn/ui
- TanStack React Query v5 (server state)
- Zustand (client state)
- Framer Motion (animations)
- React Router v6
- Axios with auth interceptors
- Lucide React (icons)

### AI Layer
- **Groq** (Llama 3.3 70B) — primary, fast text tasks
- **Gemini 2.0 Flash** — fallback + web-grounded research
- **Tavily** — fallback search API

### Infrastructure
- Docker + Docker Compose
- Nginx reverse proxy
- Multi-stage builds for production-ready images

---

## 🔑 Environment Variables

### Backend (`backend/.env`)

```bash
# Database (Supabase — use POOLER URL for connection pooling)
DATABASE_URL=postgresql+asyncpg://postgres.xxx:PWD@aws-0-region.pooler.supabase.com:6543/postgres

# Redis (Upstash)
REDIS_URL=rediss://default:PWD@xxx.upstash.io:6379

# Auth
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(32))">
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# AI Providers (all free tier)
GROQ_API_KEY=gsk_...
GOOGLE_API_KEY=AIza...
TAVILY_API_KEY=tvly-...

# App
ENVIRONMENT=development
```

### Frontend (`frontend/.env`)

```bash
VITE_API_URL=http://localhost:8000
```

See `.env.example` files for templates with inline comments.

---

## 📐 Design Decisions

### Why `follow_up_at` lives on both `leads` and `discussions`
- `discussions.follow_up_at` → audit trail (immutable, "what was decided")
- `leads.follow_up_at` → current active reminder (mutable, set by latest discussion)
- Separates historical record from current state

### Why multi-tier AI fallback
- Single provider = single point of failure
- Email generation: **Groq → Gemini → 503**
- Company enrichment: **Gemini + search → Tavily + Groq → graceful degrade**
- Mirrors the production reliability patterns used for AI agent systems

### Why optimistic UI for discussions
- Sub-50ms perceived latency
- React Query's `onMutate` snapshots state, `onError` rolls back
- Discussions appear instantly, server confirms in background

### Why Nginx in front of the frontend
- Serves static files efficiently
- Proxies `/api/*` to backend → zero CORS configuration needed
- Production-grade caching headers and gzip compression

### Why JWT over sessions
- Stateless backend (horizontally scalable)
- Single localStorage token, axios interceptor handles attachment
- 401 responses auto-redirect to login

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Create user |
| `POST` | `/api/auth/login` | OAuth2 password flow |
| `GET` | `/api/auth/me` | Current user info |
| `GET` | `/api/leads` | List leads (filters: status, search, follow_up_today) |
| `POST` | `/api/leads` | Create lead |
| `PATCH` | `/api/leads/{id}` | Update lead |
| `DELETE` | `/api/leads/{id}` | Delete lead |
| `GET` | `/api/leads/{id}/discussions` | List discussions |
| `POST` | `/api/leads/{id}/discussions` | Add discussion |
| `POST` | `/api/ai/summarize` | AI brief from discussion history |
| `POST` | `/api/ai/score-lead` | AI lead scoring (Hot/Warm/Cold) |
| `POST` | `/api/ai/suggest-followup` | Extract follow-up timing from note |
| `POST` | `/api/ai/enrich-company` | Web-grounded company intelligence |
| `POST` | `/api/ai/generate-email` | Personalized sales email |

Full interactive docs at `http://localhost:8000/docs`

---

## 📸 Screenshots

### Backend Overview
<img width="1920" height="1080" alt="Screenshot From 2026-05-15 19-40-36" src="https://github.com/user-attachments/assets/b048c22e-e561-4cd2-ab16-80db8a2f050e" />


### Lead List with Filters
<img src="https://github.com/user-attachments/assets/07e92f0a-4e38-4be2-8dbf-c02543d7b2c4">

### Lead Dialog + Timeline
<img src="https://github.com/user-attachments/assets/d4cb2787-52aa-4313-abcc-364a6f5e6014">
<img src="https://github.com/user-attachments/assets/23666b71-1465-425c-8d7d-032dcf68ecd4">
<img src="https://github.com/user-attachments/assets/d2be0a0b-9bb0-49c4-8ff6-4f6e431bd6db">

### AI Summary
<img src="https://github.com/user-attachments/assets/8a1cc168-1274-42f0-8dc3-2a622dfe4328">

### AI Score Card
<img src="https://github.com/user-attachments/assets/9504fcf6-7add-446e-a140-8e8a1fd9186d">

### AI Follow-up Suggestion
<img src="https://github.com/user-attachments/assets/03dd7ccf-4133-48ef-ad55-15c8e9652809">

### Email Generator
<img src="https://github.com/user-attachments/assets/4f8c5fa2-26ea-449f-b160-e7d5cc6ba513">

---

## 📁 Project Structure

```text
LeadFlow/
├── backend/
│   ├── app/
│   │   ├── core/          # Config, database, logging, redis
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic + AI integrations
│   │   ├── routes/        # FastAPI route handlers
│   │   └── main.py        # App factory
│   ├── tests/             # 12 passing tests
│   ├── Dockerfile
│   ├── requirements.txt
│   └── seed.py
├── frontend/
│   ├── src/
│   │   ├── components/    # Modular React components
│   │   ├── hooks/         # React Query hooks
│   │   ├── store/         # Zustand stores
│   │   ├── lib/           # axios + utilities
│   │   └── App.jsx
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## 🐳 Deployment Readiness

The Docker setup is intentionally production-ready. The same images can be deployed to:

- Render
- Railway
- Fly.io
- AWS ECS / Google Cloud Run
- Any Docker-compatible platform

Only environment variables need to be injected at the platform level. No code changes required.

---

## 📝 Notes

- **AI failures are non-blocking** — the core CRM continues working even if all AI providers are down
- **Backend stays on free tier** — Supabase + Upstash + free AI APIs cost $0 to run
- **Frontend is a true SPA** — single screen, modal-driven, no page refreshes
- **All design decisions documented** above and inline in code

---

## 👤 Author

**Mayank Dewangan**

Built for the Es Magico Fullstack Intern assessment.

- GitHub: <a href="https://github.com/MayankDew08">@MayankDew08</a>
