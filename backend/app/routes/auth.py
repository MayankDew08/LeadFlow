from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth import create_access_token, verify_tokens
import logging
from app.core.log_format import JSONFormatter

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("goals_router")
if not logger.handlers:
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/auth", tags=["auth"])

# ── Password Hashing ─────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── OAuth2 Scheme ─────────────────────────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ── Helper Functions ──────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


# ── Get Current User Dependency ───────────────────────────────────────────────
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    email = verify_tokens(token)

    user = await get_user_by_email(db=db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


# ── POST /auth/register ──────────────────────────────────────────────────────
@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    # Check if email already exists
    existing = await get_user_by_email(db=db, email=payload.email)
    if existing:
        logger.warning({
            "event": "registration_failed",
            "reason": "email_exists",
            "error_type":"Bad Request",
            "email": payload.email,
        })
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user = User(
        name=payload.name,
        email=payload.email,
        password=hash_password(payload.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info({
        "event": "user_registered successfully",
        "user_id": user.id,
        "email": user.email,
    })
    return user


# ── POST /auth/login ─────────────────────────────────────────────────────────
@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    # OAuth2PasswordRequestForm uses "username" field
    # We treat it as email
    user = await get_user_by_email(db=db, email=form_data.username)

    if not user:
        logger.warning({
            "event": "login_failed",
            "reason": "invalid_credentials",
            "error_type":"Unauthorized",
            "email": form_data.username,
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    

    if not verify_password(form_data.password, user.password):
        logger.warning({
            "event": "login_failed",
            "reason": "invalid_credentials",
            "error_type":"Unauthorized",
            "email": form_data.username,
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create JWT token with email as subject
    access_token = create_access_token(data={"sub": user.email})

    logger.info({
        "event": "login_successful",
        "user_id": user.id,
        "email": user.email,
    })

    return {"access_token": access_token, "token_type": "bearer"}


# ── GET /auth/me ──────────────────────────────────────────────────────────────
@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user