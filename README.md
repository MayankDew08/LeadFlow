<img width="1920" height="1080" alt="Screenshot From 2026-05-15 19-45-52" src="https://github.com/user-attachments/assets/c7810637-9993-4131-ade4-38085aed7967" /># LeadFlow CRM

LeadFlow is a production-style CRM for sales reps with a complete backend and an upgraded frontend focused on speed, clarity, and AI-assisted workflows.

## What We Built

### Core CRM Experience
- JWT authentication (login/signup/logout)
- Lead list with status filters and search
- Today’s follow-ups section
- Lead timeline dialog with discussion history
- Add lead flow
- Add discussion + optional follow-up datetime
- Lead status updates
- Optimistic updates and overdue highlighting

### AI Features Added (Frontend Integration)

#### 1) Company Enrichment (Add Lead Modal)
- Calls `POST /api/ai/enrich-company`
- User enters company name and clicks **Enrich**
- Shows intelligence card with:
  - company overview
  - industry/size/HQ/website/founded
  - recent news
  - pain points (sales angles)
- Includes loading, error, dismiss, and `ai_available` fallback states

#### 2) AI Lead Intelligence (Lead Dialog)
- **AI Summary** via `POST /api/ai/summarize`
- **AI Score** via `POST /api/ai/score-lead`
  - compact badge on lead cards for scanability
  - detailed score card in dialog with:
    - score meaning
    - backend reasoning
    - recommended action
  - refresh support + cache invalidation
- **AI Suggest Follow-up** via `POST /api/ai/suggest-followup`
  - suggests follow-up time from note text
  - pre-fills follow-up controls when suggestion exists

#### 3) Email Generation (Lead Dialog)
- Calls `POST /api/ai/generate-email`
- Purpose + tone + optional context inputs
- Generated subject/body preview
- Copy subject/body/all actions
- `mailto:` deep-link open
- Robust newline normalization for body formatting (`\n` rendering fixed)
- Handles provider failure/error states gracefully

## Tech Stack

### Frontend
- React 18 + Vite
- TailwindCSS
- Framer Motion
- TanStack React Query v5
- Zustand
- Axios with auth interceptors
- React Router v6
- Lucide icons

### Backend (Already Complete, Not Modified)
- FastAPI
- SQLAlchemy
- PostgreSQL (Supabase)
- JWT auth
- API prefix: `/api`

## Environment Setup

### Frontend `.env`
Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_DEFAULT_SENDER_EMAIL=
```

### Frontend `.env.example`
Included and commit-safe at `frontend/.env.example`.

## Run Locally

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Media

All screenshots can be placed in `media/`.

### Backend Overview
![Backend Overview](media/BACKEND_OVERVIEW.png)

### Login / Signup
![Auth Screens](media/AUTH.png)

### Lead List + Filters
![Lead List](media/LEAD_LIST.png)
<img width="1920" height="1080" alt="Screenshot From 2026-05-15 19-48-29" src="https://github.com/user-attachments/assets/07e92f0a-4e38-4be2-8dbf-c02543d7b2c4" />


### Lead Dialog + Timeline
![Lead Dialog](media/LEAD_DIALOG.png)

### AI Summary
![AI Summary]
<img width="1920" height="1080" alt="Screenshot From 2026-05-15 22-07-33" src="https://github.com/user-attachments/assets/8a1cc168-1274-42f0-8dc3-2a622dfe4328" />


### AI Score Card
![AI Score Card]
<img width="1920" height="1080" alt="Screenshot From 2026-05-15 22-07-11" src="https://github.com/user-attachments/assets/9504fcf6-7add-446e-a140-8e8a1fd9186d" />


### AI Suggest Follow-up
![AI Follow-up Suggestion]
<img width="1920" height="1080" alt="Screenshot From 2026-05-15 22-07-33" src="https://github.com/user-attachments/assets/03dd7ccf-4133-48ef-ad55-15c8e9652809" />


### Email Generator Modal
![Email Generator]
<img width="1920" height="1080" alt="Screenshot From 2026-05-15 22-08-11" src="https://github.com/user-attachments/assets/4f8c5fa2-26ea-449f-b160-e7d5cc6ba513" />



## Notes
- Backend code/contracts were preserved.
- AI errors are non-blocking; core CRM actions continue to work.
- UI additions follow existing Tailwind design language and motion patterns.
