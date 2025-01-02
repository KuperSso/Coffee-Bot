from sqlalchemy import Column, Integer, ForeignKey, BigInteger, Boolean
from backend.database import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(Integer, unique=True, nullable=False)
    tg_id = Column(BigInteger, unique=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)