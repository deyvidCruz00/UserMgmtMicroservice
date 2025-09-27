from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerRepository:
    """
    Repositorio para operaciones CRUD de Customer
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_customer(self, customer: CustomerCreate) -> Optional[Customer]:
        """
        Crear un nuevo cliente
        
        Args:
            customer: Datos del cliente a crear
            
        Returns:
            Customer creado o None si hay error
        """
        try:
            db_customer = Customer(
                document=customer.document,
                firstname=customer.firstname,
                lastname=customer.lastname,
                address=customer.address,
                phone=customer.phone,
                email=customer.email
            )
            self.db.add(db_customer)
            self.db.commit()
            self.db.refresh(db_customer)
            return db_customer
        except IntegrityError:
            self.db.rollback()
            return None
        except Exception as e:
            self.db.rollback()
            raise e
    
    def get_customer_by_id(self, customer_id: int) -> Optional[Customer]:
        """
        Buscar cliente por ID
        
        Args:
            customer_id: ID del cliente
            
        Returns:
            Customer encontrado o None
        """
        return self.db.query(Customer).filter(Customer.id == customer_id).first()
    
    def get_customer_by_document(self, document: str) -> Optional[Customer]:
        """
        Buscar cliente por documento
        
        Args:
            document: Documento del cliente
            
        Returns:
            Customer encontrado o None
        """
        return self.db.query(Customer).filter(Customer.document == document).first()
    
    def get_customer_by_email(self, email: str) -> Optional[Customer]:
        """
        Buscar cliente por email
        
        Args:
            email: Email del cliente
            
        Returns:
            Customer encontrado o None
        """
        return self.db.query(Customer).filter(Customer.email == email).first()
    
    def update_customer(self, customer_id: int, customer_data: CustomerUpdate) -> Optional[Customer]:
        """
        Actualizar un cliente
        
        Args:
            customer_id: ID del cliente a actualizar
            customer_data: Datos a actualizar
            
        Returns:
            Customer actualizado o None si no existe
        """
        try:
            db_customer = self.get_customer_by_id(customer_id)
            if not db_customer:
                return None
            
            # Actualizar solo los campos que no son None
            update_data = customer_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if value is not None:
                    setattr(db_customer, field, value)
            
            self.db.commit()
            self.db.refresh(db_customer)
            return db_customer
        except IntegrityError:
            self.db.rollback()
            return None
        except Exception as e:
            self.db.rollback()
            raise e
    
    def delete_customer(self, customer_id: int) -> bool:
        """
        Eliminar un cliente
        
        Args:
            customer_id: ID del cliente a eliminar
            
        Returns:
            True si se eliminó correctamente, False si no existe
        """
        try:
            db_customer = self.get_customer_by_id(customer_id)
            if not db_customer:
                return False
            
            self.db.delete(db_customer)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            raise e