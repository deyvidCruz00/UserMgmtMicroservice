from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Union

from app.database.connection import get_db
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import (
    CustomerCreate, 
    CustomerUpdate, 
    CustomerResponse, 
    CreateCustomerResponse,
    CustomerNotFound
)

router = APIRouter(prefix="/customer", tags=["customer"])


@router.post("/createcustomer", response_model=CreateCustomerResponse)
async def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    """
    Crear un nuevo cliente
    
    Args:
        customer: Datos del cliente a crear
        db: Sesión de base de datos
        
    Returns:
        Respuesta indicando si la creación fue exitosa
    """
    try:
        customer_repo = CustomerRepository(db)
        
        # Verificar si ya existe un cliente con ese documento o email
        existing_customer_by_doc = customer_repo.get_customer_by_document(customer.document)
        if existing_customer_by_doc:
            return CreateCustomerResponse(
                createCustomerValid=False,
                message="A customer with this document already exists"
            )
        
        existing_customer_by_email = customer_repo.get_customer_by_email(customer.email)
        if existing_customer_by_email:
            return CreateCustomerResponse(
                createCustomerValid=False,
                message="A customer with this email already exists"
            )
        
        # Crear el cliente
        new_customer = customer_repo.create_customer(customer)
        if new_customer:
            return CreateCustomerResponse(
                createCustomerValid=True,
                message="Customer created successfully",
                customer_id=new_customer.id
            )
        else:
            return CreateCustomerResponse(
                createCustomerValid=False,
                message="Failed to create customer"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/findcustomerbyid/{customer_id}", response_model=Union[CustomerResponse, CustomerNotFound])
async def find_customer_by_id(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Buscar cliente por ID
    
    Args:
        customer_id: ID del cliente a buscar
        db: Sesión de base de datos
        
    Returns:
        Datos del cliente o mensaje de no encontrado
    """
    try:
        customer_repo = CustomerRepository(db)
        customer = customer_repo.get_customer_by_id(customer_id)
        
        if not customer:
            return CustomerNotFound(message=f"Customer with ID {customer_id} not found")
        
        return CustomerResponse(
            id=customer.id,
            document=customer.document,
            firstname=customer.firstname,
            lastname=customer.lastname,
            address=customer.address,
            phone=customer.phone,
            email=customer.email
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/updateCustomer/{customer_id}", response_model=Union[CustomerResponse, CustomerNotFound])
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un cliente existente
    
    Args:
        customer_id: ID del cliente a actualizar
        customer_data: Datos a actualizar
        db: Sesión de base de datos
        
    Returns:
        Datos del cliente actualizado o mensaje de no encontrado
    """
    try:
        customer_repo = CustomerRepository(db)
        
        # Verificar si el cliente existe
        existing_customer = customer_repo.get_customer_by_id(customer_id)
        if not existing_customer:
            return CustomerNotFound(message=f"Customer with ID {customer_id} not found")
        
        # Verificar duplicados si se está actualizando documento o email
        if customer_data.document:
            existing_doc = customer_repo.get_customer_by_document(customer_data.document)
            if existing_doc and existing_doc.id != customer_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A customer with this document already exists"
                )
        
        if customer_data.email:
            existing_email = customer_repo.get_customer_by_email(customer_data.email)
            if existing_email and existing_email.id != customer_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A customer with this email already exists"
                )
        
        # Actualizar el cliente
        updated_customer = customer_repo.update_customer(customer_id, customer_data)
        
        if updated_customer:
            return CustomerResponse(
                id=updated_customer.id,
                document=updated_customer.document,
                firstname=updated_customer.firstname,
                lastname=updated_customer.lastname,
                address=updated_customer.address,
                phone=updated_customer.phone,
                email=updated_customer.email
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update customer"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )