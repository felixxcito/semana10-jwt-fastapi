from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = "clave-secreta-semana10-cambiar-en-produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(password: str) -> str:
    """Genera el hash bcrypt de una contraseña en texto plano."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara una contraseña en texto plano con su hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    """Crea un JWT firmado con SECRET_KEY que expira en `expires_minutes`."""
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Valida el token del header Authorization y devuelve los datos del usuario.

    Si el token falta, está alterado o expiró -> 401 Unauthorized.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        rol = payload.get("rol")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return {"username": username, "rol": rol}
