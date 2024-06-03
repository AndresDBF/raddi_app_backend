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

usertoken = APIRouter(tags=["Login"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

#funcion que se usara para cubrir las rutas con el token 
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials 
      
        if is_token_revoked(token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesion Cerrada")
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        
        
        email: str = payload.get("email")
        user_id: str = payload.get("id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales de Autenticacion Invalidas")
       
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Expirado")
    
#funciones utilizadas para el login
def is_token_revoked(token: str):
    with engine.connect() as conn:
        query =  conn.execute(blacklist_token.select()
                              .where(blacklist_token.c.token==token)).first()
        
        if query is not None:
            return query
        
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
       
@usertoken.post("/api/logout/")
async def logout(token: str):
    try:
        with engine.connect() as conn:
            if add_revoked_token(token) == True:
                return JSONResponse(content={"message": "Se ha Cerrado la Sesion"}, status_code=status.HTTP_200_OK)
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No se pudo realizar el cierre de sesión.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ha ocurrido un error: {e}")