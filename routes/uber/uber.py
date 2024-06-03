from fastapi import APIRouter, HTTPException, status, Form, Response, Depends
from fastapi.responses import JSONResponse, Response
from database.conection import engine
from models.seguridad.user_roles import user_roles
from models.uber.perfil_uber import perfil_uber
from routes.token.usertoken import get_current_user
from sqlalchemy import text
from sqlalchemy import select, update, delete, join
from sqlalchemy import select, func

routesuber = APIRouter(responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@routesuber.put("/api/uber/touch-online/")
async def touch_online_uber(data_user: str = Depends(get_current_user)):
    with engine.connect() as conn: 
        sts_uber = conn.execute(select(perfil_uber.c.con_per).select_from(perfil_uber).where(perfil_uber.c.fk_use_id==data_user["id"])).scalar()
        current_time = conn.execute(text("select get_current_time()")).scalar()
        if sts_uber == True:
            conn.execute(perfil_uber.update().where(perfil_uber.c.fk_use_id==data_user["id"]).values(con_per=False, updated_at=current_time))
            conn.commit()
            sts = False
            message = "Se ha desconectado el perfil de uber"
        else:
            conn.execute(perfil_uber.update().where(perfil_uber.c.fk_use_id==data_user["id"]).values(con_per=True, updated_at=current_time))
            conn.commit()
            sts = True
            message = "Se ha conectado el perfil de uber"
    return JSONResponse(content={
        "status": sts,
        "message": message
        
    }, status_code=status.HTTP_200_OK)
    
