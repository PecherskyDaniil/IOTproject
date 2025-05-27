from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session
import hashlib
import socket
import logging
import sys
import uvicorn
from logging.handlers import TimedRotatingFileHandler
import requests
from DB import crud
from DB.devices import models as devicesmodels
from DB.devices import schemas as devicesschemas
from DB.users import models as usersmodels
from DB.users import schemas as usersschemas

from DB.database import SessionLocal, engine


usersmodels.Base.metadata.create_all(bind=engine)
devicesmodels.Base.metadata.create_all(bind=engine)

FORMATTER_STRING = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
FORMATTER = logging.Formatter(FORMATTER_STRING)
LOG_FILE = "./Logs/API.log"

with open("./TelegramBot/token.txt") as f:
    token=f.read()

def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)

    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight',encoding='utf-8')
    file_handler.setFormatter(FORMATTER)
    logger.addHandler(file_handler)
    return logger


app = FastAPI()
async def start_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000)
    server = uvicorn.Server(config)
    await server.serve()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/create")
async def create_user(request: Request, user: usersschemas.UserCreate, db: Session = Depends(get_db)):
    logger = get_logger("create_user")
    db_user = crud.get_users_by_chat_id(db, chat_id=user.chat_id)
    if db_user:
        logger.error("Entered Chat id already registered")
        raise HTTPException(status_code=400, detail="Chat already registered")
    else:
        logger.debug("Chat verifed")
    db_user=crud.create_user(db=db, user=user)
    logger.info('New user "'+db_user.name+'" created')
    return {"name":db_user.name}

@app.post("/devices/create")
async def create_device(request: Request, device: devicesschemas.DeviceCreate, db: Session = Depends(get_db)):
    logger = get_logger("create_device")
    db_device = crud.get_device_by_hash(db, hash=device.unique_hash)
    if db_device:
        logger.error("Entered hash already registered")
        raise HTTPException(status_code=400, detail="Hash already registered")
    else:
        logger.debug("Hash verifed")
    db_device=crud.create_device(db=db, device=device)
    logger.info('New device "'+db_device.device_name+'" created')
    return {"name":db_device.device_name}

@app.post("/devices/data/update")
async def update_data(request: Request, data:dict, db: Session = Depends(get_db)):
    print(data)
    logger = get_logger("update_data")
    logger.info("Sent request to update data from device")
    db_device=crud.get_device_by_hash(db=db,hash=data["hash"])
    result=crud.insert_device_data(db=db,device_id=db_device.id,turbidity=data["turbidity"],waterlevel=data["waterlevel"])
    logger.info('Data for "'+db_device.device_name+'" updated')
    return {"name":result.device_name}


@app.get("/users/", response_model=list[usersschemas.User])
async def read_users(request: Request,skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logger = get_logger("get_user")
    users = crud.get_users(db, skip=skip, limit=limit)
    logger.info("Users returned")
    return users

@app.get("/devices/", response_model=list[devicesschemas.Device])
async def read_devices(request: Request,skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logger = get_logger("get_device")
    devices = crud.get_devices(db, skip=skip, limit=limit)
    logger.info("Devices returned")
    return devices

@app.get("/devices/feed")
async def read_users(request: Request,hash:str, db: Session = Depends(get_db)):
    logger = get_logger("get_device_feed")
    logger.info(f"Sent request to get feed data from device {hash}")
    db_device=crud.get_device_by_hash(db=db,hash=str(hash))
    logger.info('Feed data for "'+db_device.device_name+'" was sent')
    return {"feed_interval":db_device.feed_interval}
@app.post("/devices/alarm")
async def send_alarm_user(request: Request, db: Session = Depends(get_db)):#, data:dict):
    logger = get_logger("device_send_alarm")
    data=await request.json()
    db_device=crud.get_device_by_hash(db,hash=data["hash"])
    if not(db_device):
        logger.error("Entered device not found")
        raise HTTPException(status_code=400, detail="device not found")
    else:
        logger.debug("device found")
    print(db_device)
    db_user = crud.get_user_by_id(db,db_device.user_id)
    if not(db_user):
        logger.error("Entered user not found")
        raise HTTPException(status_code=400, detail="user not found")
    else:
        logger.debug("user found")
    chat_id = db_user.chat_id
    message = "Девайс \""+db_device.device_name+"\" отправил сообщение: "+data["message"]
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    print(requests.get(url).json())
    logger.info('Alarm sended to '+db_user.name+'"')
    return {"name":db_user.name}