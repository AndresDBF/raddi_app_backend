import setuptools
from fastapi import FastAPI
from database.conection import engine
#importacion de modelos
from models.seguridad.blacklist_token import blacklist_token
from models.seguridad.usuarios import usuarios
from models.seguridad.roles import roles
from models.seguridad.user_roles import user_roles
from models.seguridad.imagen_usuario import imagen_usuario
from models.seguridad.datos_identidad import datos_identidad
from models.general.categoria import categorias
from models.general.lval import lval

#importacion de middlewares
from middlewares.usuarios.register import RegUserValidationException, RegUser_validation_exception_handler
from middlewares.uber.register import RegUberValidationException, RegUber_validation_exception_handler
from middlewares.clientes.register import RegCustomerValidationException, RegCustomer_validation_exception_handler

#importacion de rutas 
from routes.roles import routerol
from routes.login.register import registeruser
from routes.login.login import login
#importaciones adicionales
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.title = "Documentación RaddiApp"
@app.get("/")
async def root():
    
    return setuptools.__version__
#---------------------------------------rutas estaticas ---------------------------------------------------
#registros del usuario
app.mount("/static/img/profile", StaticFiles(directory="static/img/profile"), name="profile_images")
app.mount("/static/img/identify/cedula", StaticFiles(directory="static/img/identify/cedula"), name="identify_images")
app.mount("/static/img/identify/selfie", StaticFiles(directory="static/img/identify/selfie"), name="selfie_images")

#documentos uber 
app.mount("/static/img/uber/license", StaticFiles(directory="static/img/uber/license"), name="license")
app.mount("/static/img/uber/property", StaticFiles(directory="static/img/uber/property"), name="property")
app.mount("/static/img/uber/rcv", StaticFiles(directory="static/img/uber/rcv"), name="rcv")
app.mount("/static/img/uber/car_forward", StaticFiles(directory="static/img/uber/car_forward"), name="car_forward")
app.mount("/static/img/uber/car_side", StaticFiles(directory="static/img/uber/car_side"), name="car_side")

#documentos cliente
app.mount("/static/img/cliente/rif", StaticFiles(directory="static/img/cliente/rif"), name="rif_cliente")
app.mount("/static/img/cliente/portada", StaticFiles(directory="static/img/cliente/portada"), name="portada_cliente")

#----------------------------------------middlewares ----------------------------------------------------------
app.add_exception_handler(RegUserValidationException,RegUser_validation_exception_handler)
app.add_exception_handler(RegUberValidationException, RegUber_validation_exception_handler)
app.add_exception_handler(RegCustomerValidationException, RegCustomer_validation_exception_handler)
#-----------------------------------------rutas---------------------------------------------------------------
app.include_router(routerol, tags=["Roles"])
app.include_router(login, tags=["Login"])
app.include_router(registeruser, tags=["Login"])

