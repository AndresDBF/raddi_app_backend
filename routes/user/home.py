import os
import asyncio
from fastapi import APIRouter, Request, HTTPException, status, Depends, BackgroundTasks, WebSocket, Header
from fastapi.responses import FileResponse, JSONResponse
from fastapi.websockets import WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from database.conection import engine
from models.seguridad.usuarios import usuarios
from models.seguridad.imagen_usuario import imagen_usuario
from models.uber.conexion_uber import conexion_uber
from models.automovil.tipo_vehiculo import tipo_vehiculo
from models.uber.perfil_uber import perfil_uber

from routes.token.usertoken import get_current_user

from jose import jwt

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

@homeuser.get("/api/user/uber-maps/")
async def uber_maps(background_task: BackgroundTasks, data_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        ubers = conn.execute(select(conexion_uber.c.fk_per_ube_id,
                                    tipo_vehiculo.c.nom_tip_veh,
                                    conexion_uber.c.cor_alt,
                                    conexion_uber.c.cor_lon)
                             .select_from(conexion_uber)
                             .join(perfil_uber, conexion_uber.c.fk_per_ube_id==perfil_uber.c.id)
                             .join(tipo_vehiculo, perfil_uber.c.fk_tv_id==tipo_vehiculo.c.id)
                             .where(conexion_uber.c.con_ube==True)).fetchall()
    
    list_ubers = [
        {
            "tip_veh": row[1],
            "altitude": row[2],
            "length": row[3]
        }
        for row in ubers
    ]
    return list_ubers

async def get_user_id_from_token(websocket: WebSocket, token: str) -> int:
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=[os.getenv('ALGORITHM')])
        email = payload.get("email")
        if email:
            with engine.connect() as conn:
                user = conn.execute(select(usuarios.c.id).select_from(usuarios).where(usuarios.c.email == email)).scalar()
                if user:
                    return user
        return None  
    except Exception:
        await websocket.close() 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Se requiere el encabezado 'authorization'")


@homeuser.websocket("/ws/uber-maps/")
async def doctor(websocket: WebSocket, authorization: str = Header(None)):
    if authorization is None:
        await websocket.close() 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Se requiere el encabezado 'authorization'")
    user_id = await get_user_id_from_token(websocket, authorization)
    if not user_id:
        await websocket.close()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de autorización inválido")

    await websocket.accept()
    
    try:
        while True: 
            print("llega al while")
            with engine.connect() as conn:
                
                ubers = conn.execute(select(conexion_uber.c.fk_per_ube_id,
                                            tipo_vehiculo.c.nom_tip_veh,
                                            conexion_uber.c.cor_alt,
                                            conexion_uber.c.cor_lon)
                                    .select_from(conexion_uber)
                                    .join(perfil_uber, conexion_uber.c.fk_per_ube_id==perfil_uber.c.id)
                                    .join(tipo_vehiculo, perfil_uber.c.fk_tv_id==tipo_vehiculo.c.id)
                                    .where(conexion_uber.c.con_ube==True)).fetchall()
            list_ubers = [
                {
                    "tip_veh": row[1],
                    "altitude": row[2],
                    "length": row[3]
                }
                for row in ubers
            ]
            await websocket.send_json(list_ubers)
            data = await websocket.receive_text()
            
                        
    except WebSocketDisconnect:
        print("entra en desconexion dentro del socket")

            
             
    
    """  background_task.add_task(update_online_status_later, doc_id, 8)
    background_tasks.append(background_task) """
      
""" 
#funcion para ejecutarse en segundo plano 8 horas despues 
async def update_online_status_later(doc_id, hours):
   
        
        
        await asyncio.sleep((total_hours - datetime.utcnow()).total_seconds())
          
            with engine.connect() as conn: 
                conn.execute(experience_doctor.update().where(experience_doctor.c.user_id==doc_id).values(online=False))
                conn.commit()
            return True 
        else:
            return False
    except CancelledError:
        print(f"se ha cancelado la tarea en segundo plano del doctor {doc_id}") 

 """
