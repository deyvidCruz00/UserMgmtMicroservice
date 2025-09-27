from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document = Column(String(50), unique=True, index=True, nullable=False)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    address = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)

    def __repr__(self):
        return f"<Customer(id={self.id}, document='{self.document}', email='{self.email}')>"