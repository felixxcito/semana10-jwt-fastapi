from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from auth import create_token, get_current_user, hash_password, verify_password

app = FastAPI(title="API con JWT - Semana 10")

# "Base de datos" en memoria. Las contraseñas se guardan hasheadas, nunca en texto plano.
usuarios_db = {
    "admin": {"username": "admin", "password": hash_password("admin123"), "rol": "admin"},
    "estudiante": {"username": "estudiante", "password": hash_password("estudiante123"), "rol": "estudiante"},
}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario = usuarios_db.get(form_data.username)
    if not usuario or not verify_password(form_data.password, usuario["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # En el payload solo va información no sensible: usuario y rol (nunca la contraseña)
    token = create_token({"sub": usuario["username"], "rol": usuario["rol"]})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/publico")
def publico():
    return {"mensaje": "Endpoint público, no necesita token"}


@app.get("/privado")
def privado(usuario: dict = Depends(get_current_user)):
    return {"mensaje": f"Hola {usuario['username']}, estás autenticado", "rol": usuario["rol"]}


@app.get("/admin")
def admin(usuario: dict = Depends(get_current_user)):
    if usuario["rol"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador",
        )
    return {"mensaje": f"Bienvenido al panel de administración, {usuario['username']}"}
