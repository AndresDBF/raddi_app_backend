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
from models.seguridad.datos_identidad import datos_identidad
from models.automovil.tipo_vehiculo import tipo_vehiculo
from models.automovil.marca_vehiculo import marca_vehiculo
from models.automovil.modelo_vehiculo import modelo_vehiculo


from middlewares.usuarios.register import RegisterUserForm, RegUserValidationException
from middlewares.uber.register import RegisterUberForm, RegUberValidationException

from routes.compress_image import compress_image

from sqlalchemy import insert, select, func, text

from jose import jwt 

from passlib.context import CryptContext
from pydantic import EmailStr

from pydantic import BaseModel, ValidationError, validator

from typing import Optional

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

async def create_new_user(request: Request, username: str, email: EmailStr, password: str, name: str, last_name: str, phone: int, gender: str, image: UploadFile):
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
        try:
            new_user = text(f"select seguridad.nuevo_usuario('{username}', '{email}', '{hashed_password}', '{name}', '{last_name}', '{str(phone)}', '{gender}')")
            user_id = conn.execute(new_user).scalar()
            conn.commit()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ha ocurrido un error inesperado al crear el usuario")
        
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
            
            if len(content_profile_image) > 1 * 1024 * 1024:  # Si la imagen pesa más de 1 MB
                content_profile_image = await compress_image(content_profile_image)
                
            with open(f"static/img/profile/{pr_image_profile}.png", "wb") as file_ident:
                file_ident.write(content_profile_image)
            
            created_at = conn.execute(text("select get_current_time()")).scalar()
            
            conn.execute(imagen_usuario.insert().values(fk_use_id=user_id, img_ori= image.filename, img_enc=pr_image_profile, created_at=created_at ))
            conn.commit()     
            
            file_path_prof = f".static/img/profile/{pr_image_profile}.png"
            image_ident = FileResponse(file_path_prof)  
            
            base_url = str(request.base_url)
            image_url = f"{base_url.rstrip('/')}/static/img/profile/{pr_image_profile}.png"
            return user_id
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

@registeruser.post("/api/user/register/")
async def user_register(request: Request,
                        username: str = Form(...),
                        email: EmailStr = Form(...),
                        password: str = Form(...),
                        name: str = Form(...),
                        last_name: str = Form(...),
                        phone: int = Form(...),
                        gender: str = Form(...),
                        image: UploadFile = File(...)
):
    create_new_user(request, username, email, password, name, last_name, phone, gender, image)
    
    return JSONResponse(content={
                "saved": True,
                "message": "Se ha registrado el usuario"
            }, status_code=status.HTTP_201_CREATED)       
    

@registeruser.post("/api/uber/register/")       
async def uber_register(request: Request,
                        username: str = Form(...),
                        email: EmailStr = Form(...),
                        password: str = Form(...),
                        name: str = Form(...),
                        last_name: str = Form(...),
                        phone: int = Form(...),
                        gender: str = Form(...),
                        car_plate: str = Form(...),
                        car_type: str = Form(...),
                        year: str = Form(...),
                        air: bool = Form(...),
                        color: str = Form(...),
                        image: UploadFile = File(...),
                        license: UploadFile = File(...),
                        property_title: UploadFile = File(...),
                        rcv: UploadFile = File(...),
                        car_forward: UploadFile = File(...),
                        car_side: UploadFile = File(...)
):
    user_id = create_new_user(request, username, email, password, name, last_name, phone, gender, image)
    #validando en el middleware de registro del uber  
    try:
        form_data = RegisterUberForm(car_plate=car_plate, car_type=car_type, year=year, color=color)
    except ValidationError as e:
        errors = e.errors()
        raise RegUberValidationException(
            field=errors[0].get('loc')[0],
            details=errors[0].get('msg')
        )
    
    #insertando los datos 
    
    
    #insertando los documentos de identidad
    with engine.connect() as conn:
        try:
            #validando los archvis 
            if license.filename[-4:] not in [".jpg", ".png", ".pdf"]:
                if license.filename[-5:] not in [".jpeg"]:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La licencia de conducir debe ser una imagen JPEG, JPG, PNG o archivo PDF ")
            if property_title.filename[-4:] not in [".jpg", ".png", ".pdf"]:
                if property_title.filename[-5:] not in [".jpeg"]:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El título de propiedad debe ser una imagen JPEG, JPG, PNG o archivo PDF ")
            if rcv.filename[-4:] not in [".jpg", ".png", ".pdf"]:
                if rcv.filename[-5:] not in [".jpeg"]:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El seguro RCV debe ser una imagen JPEG, JPG, PNG o archivo PDF ")
            if car_forward.filename[-4:] not in [".jpg", ".png", ".pdf"]:
                if car_forward.filename[-5:] not in [".jpeg"]:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La foto frontal del vehiculo debe ser una imagen JPEG, JPG, PNG")
            if car_side.filename[-4:] not in [".jpg", ".png", ".pdf"]:
                if car_side.filename[-5:] not in [".jpeg"]:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La foto lateral del vehiculo debe ser una imagen JPEG, JPG, PNG")
            
            #leyendo el contexto de los archivos 
            content_license = await license.read()
            content_property_title = await property_title.read()
            content_rcv = await rcv.read()
            content_car_forward = await car_forward.read()
            content_car_side = await car_side.read()
            
            #transformando a random para la encriptacion 
            random_license = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            random_property_title = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            random_rcv = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            random_car_forward = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            random_car_side = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            
            pr_license  = f"{hashlib.sha256(content_license).hexdigest()}{random_license}{user_id}"
            pr_property_title  = f"{hashlib.sha256(content_property_title).hexdigest()}{random_property_title}{user_id}"
            pr_rcv  = f"{hashlib.sha256(content_rcv).hexdigest()}{random_rcv}{user_id}"
            pr_car_forward  = f"{hashlib.sha256(content_car_forward).hexdigest()}{random_car_forward}{user_id}"
            pr_car_side  = f"{hashlib.sha256(content_car_side).hexdigest()}{random_car_side}{user_id}"
            
            #se optimiza en caso de que el archivo pese mas de 1 mb
            if len(content_license) > 1 * 1024 * 1024:  
                content_license = await compress_image(content_license)
            if len(content_property_title) > 1 * 1024 * 1024:  
                content_property_title = await compress_image(content_property_title)
            if len(content_rcv) > 1 * 1024 * 1024:  
                content_rcv = await compress_image(content_rcv)
            if len(content_car_forward) > 1 * 1024 * 1024:  
                content_car_forward = await compress_image(content_car_forward)
            if len(content_car_side) > 1 * 1024 * 1024:  
                content_car_side = await compress_image(content_car_side)
            
#-----------------------------------INSERTAR LOS ARCHIVOS EN EL SISTEMA DE ARCHIVOS-------------------------------------------------
            #licencia de conducir 
            if license.filename[-4:] == ".pdf":
                with open(f"static/img/uber/license/{pr_license}.pdf", "wb") as file_license:
                    file_license.write(content_license)
            else:
                with open(f"static/img/uber/license/{pr_license}.png", "wb") as file_license:
                    file_license.write(content_license)
            
            #titulo de propiedad del vehiculo
            if license.filename[-4:] == ".pdf":
                with open(f"static/img/uber/license/{pr_property_title}.pdf", "wb") as file_license:
                    file_license.write(content_property_title)
            else:
                with open(f"static/img/uber/license/{pr_property_title}.png", "wb") as file_license:
                    file_license.write(content_property_title)
            
            #responsabilidad civil        
            if license.filename[-4:] == ".pdf":
                with open(f"static/img/uber/license/{pr_rcv}.pdf", "wb") as file_license:
                    file_license.write(content_rcv)
            else:
                with open(f"static/img/uber/license/{pr_rcv}.png", "wb") as file_license:
                    file_license.write(content_rcv)
            
            #foto del vehiculo de frente 
            with open(f"static/img/uber/license/{pr_car_forward}.png", "wb") as file_license:
                    file_license.write(content_car_forward)
            
            #foto del vehiculo de lateral    
            with open(f"static/img/uber/license/{pr_car_side}.png", "wb") as file_license:
                    file_license.write(content_car_side)
            
           
            
            insert_documents = text("select uber.nuevo_documento_uber()")
            conn.execute(insert_documents).scalar()
            conn.commit()
            return JSONResponse(content={
                "saved": True,
                "message": "Se han guardado los documentos correctamente"
            }, status_code=status.HTTP_201_CREATED)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ha ocurrido un error: {e}")
   
@registeruser.post("/api/user/validate-identify/")
async def upload_image(request: Request, image_ident: UploadFile = File(..., description="imagen de identidad"), image_self: UploadFile = File(..., description="imagen de selfie")):
    with engine.connect() as conn: 
        veri_admin = conn.execute(select(user_roles.c.fk_rol_id).
                                select_from(user_roles).where(user_roles.c.fk_use_id==1)).scalar()
    if veri_admin == 1:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="El administrador no debe verificar su identidad")
        
    with engine.connect() as conn:
        verify_images = conn.execute(datos_identidad.select().where(datos_identidad.c.fk_use_id==1)).first()
    #verificando que el usuario tenga cargados los archivos de identidad para que no se dupliquen 
    if verify_images:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Ya existe imagenes de identidad para este usuario")
    
    #verificando las extensiones de los archivos que sean de tipo imagen 
    
    if image_self.filename[-4:] not in [".jpg", ".png"]:
        if image_self.filename[-5:] not in [".jpeg"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La imagen de selfie debe ser de extensión JPEG, JPG o PNG")
        
    if image_ident.filename[-4:] not in [".jpg", ".png"]:
        if image_self.filename[-5:] not in [".jpeg"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La imagen de identidad debe ser de extensión JPEG, JPG o PNG")
  
    content_ident = await image_ident.read()
    content_self = await image_self.read()
       
    random_ident= ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    random_self= ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
    ident_hash = f"{hashlib.sha256(content_ident).hexdigest()}{random_ident}{1}"
    selfie_hash = f"{hashlib.sha256(content_self).hexdigest()}{random_self}{1}"

    #para comprimir la imagen 
    if len(content_ident) > 1 * 1024 * 1024:  # Si la imagen pesa más de 1 MB
        content_ident = await compress_image(content_ident)
    if len(content_self) > 1 * 1024 * 1024:  # Si la imagen pesa más de 1 MB
        content_self = await compress_image(content_self)
    with open(f"static/img/identify/cedula/{ident_hash}.png", "wb") as file_ident:
        file_ident.write(content_ident)

    with open(f"static/img/identify/selfie/{selfie_hash}.png", "wb") as file_self:
        file_self.write(content_self)   
        
    with engine.connect() as conn:
        #insertando con la funcion pl/pgsql
        try:
            
            user_ident = text(f"select seguridad.nueva_identidad('{1}','{image_self.filename}','{selfie_hash}','{image_ident.filename}','{ident_hash}')")
            ident_id = conn.execute(user_ident).scalar()
            conn.commit()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ha ocurrido un error al insertar datos: {e}")

        image_row = conn.execute(datos_identidad.select().where(datos_identidad.c.id == ident_id)).first()        
        
    file_path_ident = f"./static/img/identify/cedula/{image_row.img_ced_enc}.png"
    file_path_self = f"./static/img/identify/selfie/{image_row.img_sel_enc}.png"        

    image_ident_file = FileResponse(file_path_ident)
    image_self_file = FileResponse(file_path_self)
            
    base_url = str(request.base_url)
    image_url_ident = f"{base_url.rstrip('/')}/static/img/identify/cedula/{image_row.img_ced_enc}.png"
    image_url_self = f"{base_url.rstrip('/')}/static/img/identify/selfie/{image_row.img_sel_enc}.png"        
            
    return JSONResponse(content={
        "saved": True,
        "message": "Se han guardado las imágenes correctamente",
        "identification_image_url": image_url_ident,
        "selfie_image_url": image_url_self
    }, status_code=status.HTTP_200_OK)
    
@registeruser.get("/api/uber/list-cars/")
async def list_cars(search_query: Optional[str] = None):
    with engine.connect() as conn:
        tip_veh = conn.execute(tipo_vehiculo.select().order_by(tipo_vehiculo.c.nom_tip_veh.asc())).fetchall()
        mar_veh  = conn.execute(marca_vehiculo.select().where(marca_vehiculo.c.est_mar=='A').order_by(marca_vehiculo.c.mar_veh.asc())).fetchall()
    
    if not search_query:
        list_veh =  {
                "tip_veh": [],
                "mar_veh": [],
                "mod_veh": []
            }
        
        #itero sobre los tipos de vehiculo para agregarlos a la lista general
        data_tip_veh = []
        for tv in tip_veh:
            data_tip_veh.append(tv.nom_tip_veh)
        
        list_veh["tip_veh"] = data_tip_veh
        
        #iterando sobre la lista general de las marcas de vehiculo
        data_mar_veh = []
        for mv in mar_veh:
            data_mar_veh.append(mv.mar_veh)
        list_veh["mar_veh"] = data_mar_veh
    else:
        list_veh =  {
                "tip_veh": [],
                "mar_veh": [],
                "mod_veh": []
        }
        #itero sobre los tipos de vehiculo para agregarlos a la lista general
        data_tip_veh = []
        for tv in tip_veh:
            data_tip_veh.append(tv.nom_tip_veh)
        
        list_veh["tip_veh"] = data_tip_veh
        with engine.connect() as conn:
            mar_veh = conn.execute(marca_vehiculo.select().where(marca_vehiculo.c.mar_veh==search_query).where(marca_vehiculo.c.est_mar=='A')
                                   .order_by(marca_vehiculo.c.mar_veh.asc())).first()
            if not mar_veh:
                return list_veh
            else:
                list_veh["mar_veh"] = mar_veh.mar_veh
                mod_veh = conn.execute(modelo_vehiculo.select().where(modelo_vehiculo.c.fk_mv_id==mar_veh.id)
                                       .order_by(modelo_vehiculo.c.mod_veh.asc())).fetchall()
        
        data_mod_veh = []
        for model in mod_veh:
            data_mod_veh.append(model.mod_veh)
        list_veh["mod_veh"] = data_mod_veh
        
             
    
    return list_veh
        