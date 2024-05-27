import re
import hashlib
import string
import random
from fastapi import APIRouter, Response, status, HTTPException,  Form, UploadFile, Request, File
from fastapi.responses import JSONResponse, FileResponse

from database.conection import engine

from models.seguridad.usuarios import usuarios
from models.seguridad.roles import roles
from models.seguridad.user_roles import user_roles
from models.seguridad.imagen_usuario import imagen_usuario

from middlewares.usuarios.register import RegisterUserForm, RegUserValidationException

from sqlalchemy import insert, select, func, text

from jose import jwt 

from passlib.context import CryptContext
from pydantic import EmailStr

from pydantic import BaseModel, ValidationError, validator

from dotenv import load_dotenv

load_dotenv()

registeruser = APIRouter(responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def verify_username_email(username: str, email: str): 
    with engine.connect() as conn:        
        query_user = conn.execute(usuarios.select().where(usuarios.c.use_nam == username)).first()
        query_email = conn.execute(usuarios.select().where(usuarios.c.email == email)).first()
        if query_user is not None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este nombre de usuario no se encuentra disponible")
        if query_email is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este Correo se encuentra en uso")
        if query_email is not None and query_user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario y correo ya existen")
        else:
            return True 

@registeruser.post("/api/user/register/")
async def user_register(request: Request,
                        username: str = Form(...),
                        email: EmailStr = Form(...),
                        password: str = Form(...),
                        name: str = Form(...),
                        last_name: str = Form(...),
                        gender: str = Form(...),
                        image: UploadFile = File(...)
):
    if not re.match("^[a-zA-Z0-9]+$", username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de usuario no admite espacios y caracteres especiales")
    #recorre el middleware para verificar campos 
    try:
        form_data = RegisterUserForm(username=username, email=email, name=name, last_name=last_name, gender=gender)
    except ValidationError as e:
        errors = e.errors()
        raise RegUserValidationException(
            field=errors[0].get('loc')[0],
            details=errors[0].get('msg')
        )
    with engine.connect() as conn:
        gender = gender.title()
        name = name.title()
        last_name = last_name.title()
        #verificando que no exista un username o un email igual al ingresado
        verify_username_email(username, email)
        hashed_password = pwd_context.hash(password)
        #inserta el usuario con la funcion pl/pgsql
        new_user = text(f"select seguridad.nuevo_usuario('{username}', '{email}', '{hashed_password}', '{name}', '{last_name}', '{gender}')")
        user_id = conn.execute(new_user).scalar()
        
        conn.commit()
        if user_id == 0:
            verify_user = conn.execute(usuarios.select().where(usuarios.c.use_nam==username)).first()
            if verify_user:
              
                conn.execute(usuarios.delete().where(usuarios.c.id==verify_user.id))
                conn.commit()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ha ocurrido un error: No se ha insertado el usuario.")    
    #insertando la imagen de perfil 
    with engine.connect() as conn:
        try:
            if image.filename[-4:] not in [".jpg", ".png"]:
                if image.filename[-5:] not in [".jpeg"]:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser una imagen JPEG, JPG o PNG")
            content_profile_image = await image.read()
            
            random_image_profile = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            pr_image_profile  = f"{hashlib.sha256(content_profile_image).hexdigest()}{random_image_profile}{user_id}"
            
            with open(f"static/img/profile/{pr_image_profile}.png", "wb") as file_ident:
                file_ident.write(content_profile_image)
                                    
            created_at = conn.execute(text("select get_current_time()")).scalar()
            
            conn.execute(imagen_usuario.insert().values(fk_use_id=user_id, img_ori= image.filename, img_enc=pr_image_profile, created_at=created_at ))
            conn.commit()     
            file_path_prof = f".static/img/profile/{pr_image_profile}.png"
            image_ident = FileResponse(file_path_prof)  
            base_url = str(request.base_url)
            image_url = f"{base_url.rstrip('/')}/static/img/profile/{pr_image_profile}.png"
            return JSONResponse(content={
                "saved": True,
                "url_img": image_url,
                "message": "Se ha registrado el usuario"
            }, status_code=status.HTTP_201_CREATED)       
        except Exception as e:
            verify_user = conn.execute(usuarios.select().where(usuarios.c.id==user_id)).first()
            if verify_user:
                conn.execute(usuarios.delete().where(usuarios.c.id==verify_user.id))
                conn.commit()
            verify_image = conn.execute(imagen_usuario.select().where(imagen_usuario.c.fk_use_id==user_id)).first()
            if verify_image:
                conn.execute(imagen_usuario.delete().where(imagen_usuario.c.id==verify_image.id))
                conn.commit()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ha ocurrido un error: {e}")
         
        