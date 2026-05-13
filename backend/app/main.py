from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.lead import router as lead_router
from app.routes.discussion import router as discussion_router
from app.routes.auth import get_current_user, router as auth_router
from app.routes.user import router as user_router

app = FastAPI(
    title="LeadFlow CRM API",
    description="Production-grade Lead Management CRM",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(lead_router, prefix="/api", dependencies=[Depends(get_current_user)])
app.include_router(discussion_router, prefix="/api", dependencies=[Depends(get_current_user)])

@app.get("/")
def root():
    return {"message": "Welcome to the LeadFlow CRM API!"}

@app.get("/health")
def health():
    return {"status": "ok", "service": "leadflow-api"}