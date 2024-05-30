from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import List, Optional
from pydantic import EmailStr
from datetime import datetime

class RegisterUberForm(BaseModel):
    car_plate: str
    car_type: str
    year: str 
    color: str

    @field_validator('car_plate')
    def check_max_car_plate(cls, v, info):
        max_length = 8
        if len(v) > max_length:
            raise RegUberValidationException(field=info.field_name, details=f"La placa del vehiculo no puede exceder de {max_length} caracteres.")
        return v

    @field_validator('car_type')
    def check_max_car_type(cls, v, info):
        max_length = 30
        if len(v) > max_length:
            raise RegUberValidationException(field=info.field_name, details=f"El tipo de vehiculo no puede exceder de {max_length} caracteres.")
        return v
    
    @field_validator('year')
    def check_max_year(cls, v, info):
        max_length = 4
        if len(v) > max_length:
            raise RegUberValidationException(field=info.field_name, details=f"El año del vehiculo no puede exceder de {max_length} caracteres.")
        return v
    @field_validator('color')
    def check_max_color(cls, v, info):
        max_length = 30
        if len(v) > max_length:
            raise RegUberValidationException(field=info.field_name, details=f"El color del vehiculo no puede exceder de {max_length} caracteres.")
        return v
   

class RegUberValidationException(Exception):
    def __init__(self, field: str, details: str):
        self.field = field
        self.details = details

async def RegUber_validation_exception_handler(request: Request, exc: RegUberValidationException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"Error: {exc.details}"},
    )
