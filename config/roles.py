from fastapi import APIRouter, HTTPException, status, Form, Response, Depends
from fastapi.responses import JSONResponse, Response
from database.conection import engine
from models.seguridad.roles import roles
from models.seguridad.user_roles import user_roles
from models.general.lval import lval
from sqlalchemy import text
from sqlalchemy import select, update, delete, join
from sqlalchemy import select, func


routerol = APIRouter(tags=['Roles'], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})


@routerol.get("/api/admin/roles/user", status_code=status.HTTP_200_OK)
async def get_rules():  
    with engine.connect() as conn:
        try:
            # Consulta los roles existentes
            query = conn.execute(roles.select()).fetchall()
            if not query:
                # Llama a la función de PostgreSQL para insertar roles
                insert_roles = text("SELECT seguridad.roles()")
                result =  conn.execute(insert_roles).scalar()   
                conn.commit()

                if result == False:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se han podido insertado los roles.")
            list_roles = [
                {
                    "role_id": row[0],
                    "cod_rol": row[1],
                    "role_name": row[2]
                }
                for row in query
            ]  # Convierte los resultados en una lista de diccionarios
            return list_roles
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ha ocurrido un error: {e}")
        
#funciones para manejar globalmente 
def verify_tiprol(tiprol: str):
    tiprol = tiprol.lower()
    with engine.connect() as conn:
        if tiprol == "patient":
            role = conn.execute(roles.select().where(roles.c.role_name == tiprol)).first()
            namerole = role.role_name
            return namerole
        if tiprol == "doctor":
            role = conn.execute(roles.select().where(roles.c.role_name == tiprol)).first()
            namerole = role.role_name
            return namerole
        if tiprol == "admin":
            role = conn.execute(roles.select().where(roles.c.role_name == tiprol)).first()
            namerole = role.role_name
            return namerole