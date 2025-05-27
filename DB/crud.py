from sqlalchemy.orm import Session
import hashlib
from .devices import models as devicesmodels
from .devices import schemas as devicesschemas
from .users import models as usersmodels
from .users import schemas as usersschemas
def get_device_by_id(db: Session, device_id: int):
    return db.query(devicesmodels.Device).filter(devicesmodels.Device.id == device_id).first()

def get_device_by_hash(db: Session, hash: str):
    return db.query(devicesmodels.Device).filter(devicesmodels.Device.unique_hash == hash).first()

def get_device_by_device_name(db: Session, device_name: str):
    return db.query(devicesmodels.Device).filter(devicesmodels.Device.device_name == device_name).first()

def get_device_by_user(db: Session, user_id: int):
    return db.query(devicesmodels.Device).filter(devicesmodels.Device.user_id == user_id).all()

def update_feed_interval(db: Session, device_id: int,feed_interval:int):
    db_response=db.query(devicesmodels.Device).filter(devicesmodels.Device.id == device_id).first()
    db_response.feed_interval=feed_interval
    db.commit()
    db.refresh(db_response)
    return db_response

def create_device(db: Session, device: devicesschemas.DeviceCreate):
    db_device = devicesmodels.Device(device_name=device.device_name,user_id=device.user_id,unique_hash=device.unique_hash)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def get_user_by_id(db: Session, user_id: int):
    return db.query(usersmodels.User).filter(usersmodels.User.id == user_id).first()

def get_users_by_name(db: Session, username: str):
    return db.query(usersmodels.User).filter(usersmodels.User.name == username).all()

def get_users_by_chat_id(db: Session, chat_id: str):
    return db.query(usersmodels.User).filter(usersmodels.User.chat_id == chat_id).first()

def create_user(db: Session, user: usersschemas.UserCreate):
    db_user = usersmodels.User(name=user.name,chat_id=user.chat_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def insert_device_data(db: Session,device_id:int,turbidity:float,waterlevel:float):
    db_response=db.query(devicesmodels.Device).filter(devicesmodels.Device.id == device_id).first()
    db_response.last_turbidity=turbidity
    db_response.last_waterlevel=waterlevel
    db.commit()
    db.refresh(db_response)
    return db_response

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(usersmodels.User).offset(skip).limit(limit).all()

def get_devices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(devicesmodels.Device).offset(skip).limit(limit).all()