from fastapi import APIRouter, HTTPException, status, Form, Response, Depends
from fastapi.responses import JSONResponse, Response
from database.conection import engine
from models.seguridad.user_roles import user_roles
from models.automovil.tipo_transporte import tipo_transporte
from models.automovil.tipo_vehiculo import tipo_vehiculo
from models.uber.perfil_uber import perfil_uber
from models.translados.rutas import rutas
from routes.token.usertoken import get_current_user

from schemas.user.translate import TranslateSchema
from sqlalchemy import text
from sqlalchemy import select, update, delete, join
from sqlalchemy import select, func

from datetime import datetime, timedelta

translates = APIRouter(responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@translates.post("/api/user/create-route/", response_model=TranslateSchema)
async def touch_online_uber(translate: TranslateSchema, data_user: str = Depends(get_current_user)):
    new_translate = translate.dict()
    with engine.connect() as conn: 
        try:
            procedure = text(f"select translados.nueva_ruta({data_user["id"]}, {new_translate["altitude_1"]}, {new_translate["length_1"]}, {new_translate["altitude_2"]}, {new_translate["length_2"]})")
            print(procedure)
            conn.execute(procedure).scalar()
            conn.commit()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ha ocurrido un error al insertar los datos: {e}")
    return TranslateSchema(**new_translate)

@translates.get("/api/user/type-transport/")
async def type_vehicle(distance: float, minutes: int, type_car: str, data_user: str = Depends(get_current_user)):
    with engine.connect() as conn: 
        tip_veh =  conn.execute(select(tipo_vehiculo.c.id).select_from(tipo_vehiculo).where(tipo_vehiculo.c.nom_tip_veh==type_car)).scalar()
        print(tip_veh)
        result = conn.execute(tipo_transporte.select().where(tipo_transporte.c.fk_tv_id==tip_veh).order_by(tipo_transporte.c.nom_veh.asc())).fetchall()
        current_time = conn.execute(text("select get_current_time()")).scalar()
        time = datetime.strftime(current_time, "%H:%M:%S")
  
    return [
        {
            "tip_veh": row[2],
            "current_time": time,
            "num_passangers": row[3],
            "lapse": f"{minutes} de distancia."
        }
        for row in result
    ]
    
