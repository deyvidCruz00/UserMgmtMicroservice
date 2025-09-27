from pydantic import BaseModel
from typing import Optional


class CustomerBase(BaseModel):
    document: str
    firstname: str
    lastname: str
    address: str
    phone: str
    email: str


class CustomerCreate(CustomerBase):
    """Schema para crear un nuevo cliente"""
    pass


class CustomerUpdate(BaseModel):
    """Schema para actualizar un cliente"""
    document: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class CustomerResponse(CustomerBase):
    """Schema para la respuesta del cliente"""
    id: int

    class Config:
        orm_mode = True


class CreateCustomerResponse(BaseModel):
    """Schema para la respuesta de crear cliente"""
    createCustomerValid: bool
    message: Optional[str] = None
    customer_id: Optional[int] = None


class CustomerNotFound(BaseModel):
    """Schema para cuando no se encuentra un cliente"""
    message: str = "Customer not found"