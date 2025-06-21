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
from fastapi.middleware.cors import CORSMiddleware
import paho.mqtt.client as mqtt_client
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешает все домены (для разработки)
    allow_credentials=True,
    allow_methods=["*"],  # Разрешает все HTTP-методы (GET, POST, PUT и т.д.)
    allow_headers=["*"],  # Разрешает все заголовки
)
client = mqtt_client.Client(
   mqtt_client.CallbackAPIVersion.VERSION1, 
    'main_server'
)
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

@app.post("api/users/create")
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

@app.get("/api/users/{id}")
async def create_device(request: Request, id: int, db: Session = Depends(get_db)):
    logger = get_logger("get_device")
    db_user = crud.get_user_by_id(db,user_id=id)
    if not db_user:
        logger.error("Entered id not in db")
        raise HTTPException(status_code=400, detail="user not found")
    else:
        logger.debug("User founded")
    logger.info('Return user "'+db_user.name+'" by api')
    return {"info":db_user}

@app.post("api/devices/create")
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

@app.get("/api/devices/{deviceHash}")
async def create_device(request: Request, deviceHash: str, db: Session = Depends(get_db)):
    answer={}
    logger = get_logger("get_device")
    db_device = crud.get_device_by_hash(db, hash=deviceHash)
    if not db_device:
        logger.error("Entered hash isnt registred")
        raise HTTPException(status_code=400, detail="Device not found")
    else:
        logger.debug("device found")
    
    db_data=crud.get_last_data_by_device_hash(db,hash=deviceHash)
    db_user=crud.get_user_by_id(db,user_id=db_device.user_id)
    answer["info"]=db_device
    answer["metrics"]=db_data
    db_user=db_user.__dict__
    db_user.pop("chat_id",None)
    answer["owner"]=db_user
    
    
    logger.info('Return device "'+db_device.device_name+'" by api')
    return answer

@app.get("/api/data/get/{deviceHash}")
async def get_data_all(request:Request,deviceHash:str,limit:int=100,db: Session = Depends(get_db)):
    logger = get_logger("get_data")
    logger.info("Sent request to get data")
    db_data=crud.get_data_by_device_hash(db=db,hash=deviceHash)
    return db_data

@app.post("api/data/update")
async def update_data(request: Request, data:dict, db: Session = Depends(get_db)):
    logger = get_logger("update_data")
    logger.info("Sent request to update data from device")
    db_device=crud.get_device_by_hash(db=db,hash=data["hash"])
    result=crud.insert_device_data(db=db,device_id=db_device.id,turbidity=data["turbidity"],waterlevel=data["waterlevel"])
    logger.info('Data for "'+db_device.device_name+'" updated')
    return {"result":"updated"}


@app.get("api/users/", response_model=list[usersschemas.User])
async def read_users(request: Request,skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logger = get_logger("get_user")
    users = crud.get_users(db, skip=skip, limit=limit)
    logger.info("Users returned")
    return users

@app.get("api/devices/", response_model=list[devicesschemas.Device])
async def read_devices(request: Request,skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logger = get_logger("get_device")
    devices = crud.get_devices(db, skip=skip, limit=limit)
    logger.info("Devices returned")
    return devices

@app.get("api/devices/feed")
async def read_users(request: Request,hash:str, db: Session = Depends(get_db)):
    logger = get_logger("get_device_feed")
    logger.info(f"Sent request to get feed data from device {hash}")
    db_device=crud.get_device_by_hash(db=db,hash=str(hash))
    logger.info('Feed data for "'+db_device.device_name+'" was sent')
    return {"feed_interval":db_device.feed_interval}

@app.post("/api/data/refresh/{hash}")
async def refresh_data(request:Request,hash:str,db: Session = Depends(get_db)):
    client.connect("broker.emqx.io")
    client.loop_start()
    client.publish(f"/pech/esplamp/{hash}", f"sensors")
    client.disconnect()
    client.loop_stop()
    return {"result":"ok"}

@app.post("api/devices/alarm")
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