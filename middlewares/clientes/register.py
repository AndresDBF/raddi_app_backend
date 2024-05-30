from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import List, Optional
from pydantic import EmailStr
from datetime import datetime

class RegisterCustomerForm(BaseModel):
    name_company: str
    commercial_register: str
    rif: str
    direction: str
    phone_company: str

    @field_validator('name_company')
    def check_max_name_company(cls, v, info):
        max_length = 80
        if len(v) > max_length:
            raise RegCustomerValidationException(field=info.field_name, details=f"El nombre de la empresa no puede exceder de {max_length} caracteres.")
        return v

    @field_validator('commercial_register')
    def check_max_commercial_register(cls, v, info):
        max_length = 9
        if len(v) > max_length:
            raise RegCustomerValidationException(field=info.field_name, details=f"El registro de comercio no puede exceder de {max_length} caracteres.")
        return v
    
    @field_validator('rif')
    def check_max_rif(cls, v, info):
        max_length = 10
        if len(v) > max_length:
            raise RegCustomerValidationException(field=info.field_name, details=f"El rif no puede exceder de {max_length} caracteres.")
        return v
    @field_validator('direction')
    def check_max_direction(cls, v, info):
        max_length = 250
        if len(v) > max_length:
            raise RegCustomerValidationException(field=info.field_name, details=f"La dirección no puede exceder de {max_length} caracteres.")
        return v
    
    @field_validator('phone_company')
    def check_max_phone_company(cls, v, info):
        max_length = 20
        if len(v) > max_length:
            raise RegCustomerValidationException(field=info.field_name, details=f"El teléfono de la empresa no puede exceder de {max_length} caracteres.")
        return v
   

class RegCustomerValidationException(Exception):
    def __init__(self, field: str, details: str):
        self.field = field
        self.details = details

async def RegCustomer_validation_exception_handler(request: Request, exc: RegCustomerValidationException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": f"Error: {exc.details}"},
    )
