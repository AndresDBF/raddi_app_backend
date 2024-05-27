from typing import Union
from database.conection import engine
from models.seguridad.usuarios import usuarios
from models.seguridad.roles import roles
from models.seguridad.user_roles import user_roles
from models.seguridad.imagen_usuario import imagen_usuario
from models.general.categoria import categorias
from models.general.lval import lval

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    with engine.connect() as connection:
        usu = connection.execute(usuarios.select()).fetchall()
    return usu

