from datetime import datetime, timedelta, timezone
import os
import logging
import time

from fastapi import HTTPException, status
from authlib.jose import jwt
from authlib.jose.errors import JoseError
from dotenv import load_dotenv
from app.core.log_format import JSONFormatter
from app.core.exceptions import AuthenticationError, ValidationError

load_dotenv()  # Load environment variables from .env file

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set in environment variables")

JWT_SECRET_KEY = SECRET_KEY

# Setup logging
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("auth_service")
if not logger.handlers:
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


def create_access_token(data: dict) -> str:
    """Create a JWT access token with timing and logging."""
    start_time = time.time()
    try:
        if not isinstance(data, dict):
            raise ValidationError("Token data must be a dictionary")
        
        if "sub" not in data:
            raise ValidationError("Token data must contain 'sub' (subject/username)")
        
        header = {"alg": ALGORITHM}
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = data.copy()
        # Use numeric UNIX timestamp for `exp` to be compatible with JWT validators
        payload.update({"exp": int(expire.timestamp())})
        token = jwt.encode(header, payload, JWT_SECRET_KEY)
        if isinstance(token, bytes):
            token = token.decode("utf-8")
        
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "token_created",
            "subject": data.get("sub"),
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return str(token)
    except ValidationError as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "token_creation_validation_failed",
            "error": str(e),
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        raise
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "token_creation_failed",
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        raise AuthenticationError(f"Token creation failed: {str(e)}")


def verify_tokens(token: str) -> str:
    """Decode and validate a JWT access token and return the subject (username).

    Raises HTTPException(401) for any invalid input or failed validation.
    """
    start_time = time.time()
    try:
        if not isinstance(token, str):
            raise ValidationError("Token must be a string")

        if not token.strip():
            raise ValidationError("Token cannot be empty")
        
        try:
            claims = jwt.decode(token, JWT_SECRET_KEY)
            claims.validate()
        except JoseError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
        
        username = claims.get("sub")
        if not username:
            raise AuthenticationError("Token missing subject (username)")
        
        elapsed = (time.time() - start_time) * 1000
        logger.info({
            "event": "token_verified",
            "subject": username,
            "duration_ms": round(elapsed, 2),
            "status": "success"
        })
        return str(username)
    except (ValidationError, AuthenticationError) as e:
        elapsed = (time.time() - start_time) * 1000
        logger.warning({
            "event": "token_verification_failed",
            "reason": type(e).__name__,
            "error": str(e),
            "duration_ms": round(elapsed, 2),
            "status": "failure"
        })
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not verify credentials")
    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        logger.error({
            "event": "token_verification_error",
            "error": str(e),
            "error_type": type(e).__name__,
            "duration_ms": round(elapsed, 2),
            "status": "error"
        })
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token verification error")