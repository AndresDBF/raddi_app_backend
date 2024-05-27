from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import List, Optional
from pydantic import EmailStr
from datetime import datetime

class RegisterUserForm(BaseModel):
    username: str
    email: EmailStr
    name: str 
    last_name: str
    gender: str

    @field_validator('username')
    def check_max_username(cls, v, info):
        max_length = 20
        if len(v) > max_length:
            raise RegUserValidationException(field=info.field_name, details=f"El nombre de usuario no puede exceder de {max_length} caracteres.")
        return v

    @field_validator('email')
    def check_max_email(cls, v, info):
        max_length = 80
        if len(v) > max_length:
            raise RegUserValidationException(field=info.field_name, details=f"El email de usuario no puede exceder de {max_length} caracteres.")
        return v
    
    @field_validator('name')
    def check_max_name(cls, v, info):
        max_length = 80
        if len(v) > max_length:
            raise RegUserValidationException(field=info.field_name, details=f"El nombre no puede exceder de {max_length} caracteres.")
        return v
    @field_validator('last_name')
    def check_max_last_name(cls, v, info):
        max_length = 80
        if len(v) > max_length:
            raise RegUserValidationException(field=info.field_name, details=f"El apellido no puede exceder de {max_length} caracteres.")
        return v
    @field_validator('gender')
    def check_max_gender(cls, v, info):
        max_length = 1
        if len(v) > max_length:
            raise RegUserValidationException(field=info.field_name, details=f"El genero no puede exceder de {max_length} caracteres. Debe ingresar masculino (M) o femenino (F)")

class RegUserValidationException(Exception):
    def __init__(self, field: str, details: str):
        self.field = field
        self.details = details

async def RegUser_validation_exception_handler(request: Request, exc: RegUserValidationException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"Error: {exc.details}"},
    )
