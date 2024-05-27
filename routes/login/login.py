import os 
from fastapi import APIRouter, HTTPException, Depends, Form, status
from fastapi.responses import Response, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


from database.conection import engine

from models.seguridad.roles import roles
from models.seguridad.user_roles import user_roles
from models.seguridad.usuarios import usuarios
from models.seguridad.blacklist_token import blacklist_token

from passlib.context import CryptContext
from typing import List, Union
from pydantic import ValidationError

from sqlalchemy import select, insert, func, or_, text
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from jose import jwt, JWTError
from datetime import date, datetime, timedelta

load_dotenv()

security = HTTPBearer()

token = APIRouter(tags=["Login"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

#funcion que se usara para cubrir las rutas con el token 
"""async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    email = None
    try:
        token = credentials.credentials 
      
        if is_token_revoked(token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesion Cerrada")
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
       
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales de Autenticacion Invalidas")
        with engine.connect() as conn:
            veri_user = conn.execute(select(users.c.id, users.c.banned).select_from(users).where(users.c.email==email).where(users.c.banned==True)).scalar()
        if veri_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Expirado")
        return email
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Expirado") """

#funciones utilizadas para el login
def is_token_revoked(token: str):
    with engine.connect() as conn:
        query =  conn.execute(blacklist_token.select()
                              .where(blacklist_token.c.token==token)).first()
        
        if query is not None:
            return query

def authenticate_user(email, password):
    user = get_user(email)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se pueden validar las credenciales", headers={"www-authenticate": "Bearer"})
    if not verify_password(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No se pueden validar las credenciales", headers={"www-authenticate": "Bearer"})
    return user
def get_user(email):
    with engine.connect() as conn:
        result = conn.execute(usuarios.select().where(usuarios.c.email == email)).first()
        if result:
            #para que se devuelva el conjunto de datos de la base de datos
            return result
        return []
def verify_password(plane_password, hashed_password):

    return pwd_context.verify(plane_password,hashed_password) #verificando que el texto plano sea igual que el encriptado
def create_token(data: dict, time_expire: Union[datetime,None] = None):
    data_copy = data.copy()
    if time_expire is None:
        expires = datetime.utcnow() +  timedelta(minutes=1440)#datetime.utcnow() trae la hora de ese instante
    else:
        expires = datetime.utcnow() + time_expire
    
    data_copy.update({"exp": expires})
    token_jwt = jwt.encode(data_copy, key=os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))

    return token_jwt

#funciones utilizadas para el cierre de sesion 

def add_revoked_token(black_token: str):
    with engine.connect() as conn:
        payload = jwt.decode(black_token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        email: str = payload.get("sub")
        query = text(f"select seguridad.cierre_sesion('{black_token}')")
        print(query)
        result = conn.execute(query).scalar()
        
        conn.commit()
    return result

@token.post("/api/user/login/", status_code=status.HTTP_200_OK)
async def user_login(email: str = Form(...), password: str = Form(...)):
        try:
            with engine.connect() as conn:
                result = conn.execute(usuarios.select().where(usuarios.c.email == email)).first()
                if result is None:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no registrado")

                id = result.id
                role = conn.execute(roles.select().
                                    join(user_roles, roles.c.id == user_roles.c.fk_rol_id).
                                    where(user_roles.c.fk_use_id == id)).first()                    
                stored_password_hash = result[3]
                if pwd_context.verify(password, stored_password_hash):
                    user = authenticate_user(email, password)
                    access_token_expires = timedelta(weeks=1)
                       
                    access_token_jwt = create_token({"sub": user.email}, access_token_expires)

                    login_user = {
                        "user":{
                            "id": id,
                            "tiprol": role[2],
                        },
                        "token":{
                            "access_token": access_token_jwt,
                            "token_types": "bearer"
                        }
                    } 
                    
                    return login_user 
                else:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta")
              
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}")
        
        
@token.post("/api/logout/")
async def logout(token: str):
    try:
        with engine.connect() as conn:
            if add_revoked_token(token) == True:
                return JSONResponse(content={"message": "Se ha Cerrado la Sesion"}, status_code=status.HTTP_200_OK)
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo realizar el cierre de sesión.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ha ocurrido un error: {e}")
""" @token.post("/api/user/register_device_token/")
async def register_device_token(dev_token: str, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        user_id = conn.execute(select(users.c.id).select_from(users).where(users.c.email==current_user)).scalar()
        conn.execute(device_token.insert().values(user_id=user_id, token=dev_token))
        conn.commit()
    return {"message": "Token de usuario registrado"} """
