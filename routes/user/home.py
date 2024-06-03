import os
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from database.conection import engine
from models.seguridad.usuarios import usuarios
from models.seguridad.imagen_usuario import imagen_usuario

from routes.token.usertoken import get_current_user

homeuser = APIRouter(responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@homeuser.get("/api/user/home/")
async def user_home(request: Request, data_user: str = Depends(get_current_user)):    
    
    with engine.connect() as conn:
        
        user = conn.execute(select(usuarios.c.nom_usu, usuarios.c.ape_usu).select_from(usuarios).where(usuarios.c.id==data_user["id"])).first()
        
        # Obtener la imagen del perfil del usuario
        image_row =  conn.execute(imagen_usuario.select().where(imagen_usuario.c.fk_use_id == data_user["id"])).first()
        if image_row is not None:
            file_path = f"./static/img/profile/{image_row.img_enc}.png"
            if not os.path.exists(file_path):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La imagen de perfil no existe en el sistema de archivos")
            
            image = FileResponse(file_path)
            
            base_url = str(request.base_url)
            image_url = f"{base_url.rstrip('/')}/static/img/profile/{image_row.img_enc}.png"
            
            return {"id": data_user["id"], "name": user.nom_usu, "last_name": user.ape_usu, "image": image_url}
        return {"id": data_user["id"], "name": user.nom_usu, "last_name": user.ape_usu, "image": None}

