from datetime import datetime, timedelta, timezone
import os

from fastapi import HTTPException, status
from authlib.jose import jwt
from authlib.jose.errors import JoseError
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set")

JWT_SECRET_KEY = SECRET_KEY
def create_access_token(data: dict) -> str:
    header = {"alg": ALGORITHM}
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = data.copy()
    # Use numeric UNIX timestamp for `exp` to be compatible with JWT validators
    payload.update({"exp": int(expire.timestamp())})
    token = jwt.encode(header, payload, JWT_SECRET_KEY)
    if isinstance(token, bytes):
        return token.decode("utf-8")
    return str(token)


def verify_tokens(token: str) -> str:
    """Decode and validate a JWT access token and return the subject (username).

    Raises HTTPException(401) for any invalid input or failed validation.
    """
    if not isinstance(token, str):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token must be a string")

    try:
        claims = jwt.decode(token, JWT_SECRET_KEY)
        claims.validate()
        username = claims.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        # coerce non-string subjects to string for downstream callers that expect a username
        return str(username)
    except JoseError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not verify credentials")