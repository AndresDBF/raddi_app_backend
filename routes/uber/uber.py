from fastapi import APIRouter, HTTPException, status, Form, Response, Depends
from fastapi.responses import JSONResponse, Response
from database.conection import engine
from models.seguridad.user_roles import user_roles
from models.uber.perfil_uber import perfil_uber
from models.uber.conexion_uber import conexion_uber
from routes.token.usertoken import get_current_user
from sqlalchemy import text
from sqlalchemy import select, update, delete, join
from sqlalchemy import select, func
from sqlalchemy.exc import InternalError 

routesuber = APIRouter(responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@routesuber.put("/api/uber/touch-online/")
async def touch_online_uber(altitude: float, length: float, data_user: str = Depends(get_current_user)):
    with engine.connect() as conn: 
        try:
            uber_id = conn.execute(select(perfil_uber.c.id).select_from(perfil_uber).where(perfil_uber.c.fk_use_id==data_user["id"])).scalar()
            sts_uber = conn.execute(select(conexion_uber.c.con_ube).select_from(conexion_uber).where(conexion_uber.c.fk_per_ube_id==uber_id)).scalar()
            current_time = conn.execute(text("select get_current_time()")).scalar()
            if sts_uber is None:
                conn.execute(conexion_uber.insert().values(fk_per_ube_id=uber_id, con_ube=True,
                                                        cor_alt=altitude, cor_lon=length, created_at=current_time))
                conn.commit()
                sts = True
                message = "Se ha conectado el perfil del uber"
            elif sts_uber == True:
                conn.execute(conexion_uber.update().where(conexion_uber.c.fk_per_ube_id==uber_id).values(con_ube=False, updated_at=current_time))
                conn.commit()
                sts = False
                message = "Se ha desconectado el perfil de uber"
            else:
                conn.execute(conexion_uber.update().where(conexion_uber.c.fk_per_ube_id==uber_id).values(con_ube=True, updated_at=current_time))
                conn.commit()
                sts = True
                message = "Se ha conectado el perfil de uber"
            return JSONResponse(content={
                "status": sts,
                "message": message
                
            }, status_code=status.HTTP_200_OK)
    
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ha ocurrido un error: {e}")
    
