from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
import datetime
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    chat_id= Column(String, unique=True, index=True)
    name=Column(String)
    devices=relationship("Device", back_populates="user")