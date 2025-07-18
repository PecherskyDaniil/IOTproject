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

def delete_device(db:Session,device_id:int):
    db_device=db.query(devicesmodels.Device).get(device_id)
    db.delete(db_device)
    db.commit()
    return db_device

def insert_device_data(db: Session,device_id:int,turbidity:float,waterlevel:float):
    db_data=devicesmodels.DeviceData(device_id=device_id,turbidity=turbidity,waterlevel=waterlevel)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data
def get_data_by_device_id(db:Session,device_id:int,limit:int=100):
    return db.query(devicesmodels.DeviceData).filter(devicesmodels.DeviceData.device_id == device_id).order_by(devicesmodels.DeviceData.created).limit(limit).all()

def get_data_by_device_hash(db:Session,hash:str,limit:int=100):
    return get_data_by_device_id(db,db.query(devicesmodels.Device).filter(devicesmodels.Device.unique_hash==hash).first().id,limit)

def get_last_data_by_device_id(db:Session,device_id:int):
    return db.query(devicesmodels.DeviceData).filter(devicesmodels.DeviceData.device_id == device_id).order_by(devicesmodels.DeviceData.created).first()

def get_last_data_by_device_hash(db:Session,hash:str):
    return get_last_data_by_device_id(db,db.query(devicesmodels.Device).filter(devicesmodels.Device.unique_hash==hash).first().id)

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(usersmodels.User).offset(skip).limit(limit).all()

def get_devices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(devicesmodels.Device).offset(skip).limit(limit).all()

def get_data(db: Session, skip: int = 0, limit: int = 100):
    return db.query(devicesmodels.DeviceData).offset(skip).limit(limit).all()