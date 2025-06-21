from sqlalchemy import Boolean, Column, ForeignKey, Integer,TIMESTAMP, String,Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import datetime
from ..database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    unique_hash = Column(String, unique=True, index=True)
    device_name=Column(String)
    user_id=Column(Integer, ForeignKey("users.id"))
    data=relationship("DeviceData")
    last_changed=Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())
    feed_interval=Column(Integer,default=6)
    user = relationship("User", back_populates="devices")

class DeviceData(Base):
    __tablename__ = "devicedatas"

    id = Column(Integer, primary_key=True)
    device_id=Column(Integer, ForeignKey('devices.id'))
    turbidity=Column(Float,default=0.0)
    waterlevel=Column(Float,default=0.0)
    created=Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())
    