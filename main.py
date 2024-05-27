from fastapi import FastAPI
from database.conection import engine
#importacion de modelos
from models.seguridad.blacklist_token import blacklist_token
from models.seguridad.usuarios import usuarios
from models.seguridad.roles import roles
from models.seguridad.user_roles import user_roles
from models.seguridad.imagen_usuario import imagen_usuario
from models.general.categoria import categorias
from models.general.lval import lval

#importacion de middlewares
from middlewares.usuarios.register import RegUserValidationException, RegUser_validation_exception_handler

#importacion de rutas 
from routes.roles import routerol
from routes.login.register import registeruser
from routes.login.login import token
#importaciones adicionales
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.title = "Documentación RaddiApp"

#---------------------------------------rutas estaticas ---------------------------------------------------

app.mount("/static/img/profile", StaticFiles(directory="static/img/profile"), name="profile_images")

#----------------------------------------middlewares ----------------------------------------------------------
app.add_exception_handler(RegUserValidationException,RegUser_validation_exception_handler)
#-----------------------------------------rutas---------------------------------------------------------------
app.include_router(routerol, tags=["Roles"])
app.include_router(token, tags=["Login"])
app.include_router(registeruser, tags=["Login"])

