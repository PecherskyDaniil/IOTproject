import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from sqlalchemy.orm import Session
from aiogram.filters.command import Command,CommandObject
from pathlib import Path
from aiogram.types import ContentType, File,FSInputFile,Message,CallbackQuery,InputFile,InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from logging.handlers import TimedRotatingFileHandler
import time
import hashlib
import os
import json
import requests
import sys
from DB import crud
from DB.devices import models as devicesmodels
from DB.devices import schemas as devicesschemas
from DB.users import models as usersmodels
from DB.users import schemas as usersschemas
from DB.database import SessionLocal, engine
import paho.mqtt.client as mqtt_client
usersmodels.Base.metadata.create_all(bind=engine)
devicesmodels.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_keyboard_devices_get(device_names,device_ids):
    buttons = [] 
    for ind,device in enumerate(device_names):
        buttons.append([types.InlineKeyboardButton(text=device, callback_data="get_device_"+str(device_ids[ind]))])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
def get_keyboard_devices_update(device_names,device_ids):
    buttons = [] 
    for ind,device in enumerate(device_names):
        buttons.append([types.InlineKeyboardButton(text=device, callback_data="update_device_"+str(device_ids[ind]))])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
FORMATTER_STRING = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
FORMATTER = logging.Formatter(FORMATTER_STRING)
LOG_FILE = "./Logs/Bot.log"


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)

    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight',encoding='utf-8')
    file_handler.setFormatter(FORMATTER)
    logger.addHandler(file_handler)
    logger = logging.LoggerAdapter(logger)
    return logger
with open('./TelegramBot/token.txt','r') as file:
    token=file.read()
bot = Bot(token=token)
# Диспетчер
dp = Dispatcher()
client = mqtt_client.Client(
   mqtt_client.CallbackAPIVersion.VERSION1, 
    'main_server'
)

@dp.message(Command('register'))
async def register_device(
        message: Message,
        command: CommandObject
):
    # Если не переданы никакие аргументы, то
    # command.args будет None
    logger = get_logger("create_device")
    if command.args is None:
        logger.error("Command doesn't have parametres")
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    # Пробуем разделить аргументы на две части по первому встречному пробелу
    try:
        name, hash = command.args.split(" ", maxsplit=1)
    # Если получилось меньше двух частей, вылетит ValueError
    except ValueError:
        logger.error("Wrong command format")
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/register <name> <hash>"
        )
        return
    
    db=SessionLocal()
    db_device = crud.get_device_by_hash(db, hash=hash)
    if db_device:
        logger.error("Entered hash already registered")
        db.close()
        await message.answer(
        "Данный hash уже был зарегистрирован!"
        )
        return
    else:
        logger.debug("Hash verifed")
    db_users=crud.get_users_by_chat_id(db,chat_id=str(message.chat.id))
    print(db_users)
    if not(db_users):
        db_user=crud.create_user(db,user=usersschemas.UserCreate(chat_id=str(message.chat.id),name=message.from_user.full_name))
        user_id=db_user.id
        username=db_user.name
    else:
        user_id=db_users.id
        username=db_users.name
    db_device=crud.create_device(db=db, device=devicesschemas.DeviceCreate(device_name=name,unique_hash=hash,user_id=user_id))
    device_name=db_device.device_name
    device_hash=db_device.unique_hash
    logger.info(f"Device {db_device.device_name} from user {username} was registred")
    db.close()
    await message.answer(
        "Девайс добавлен!\n"
        f"Имя: {device_name}\n"
        f"Hash: {device_hash}"
    )
@dp.message(Command('devices'))
async def get_list_of_devices(
        message: Message,
        command: CommandObject
):
    # Если не переданы никакие аргументы, то
    # command.args будет None
    logger = get_logger("get_list_devices")
    db=SessionLocal()
    db_user=crud.get_users_by_chat_id(db,chat_id=str(message.chat.id))
    if not(db_user):
        logger.error("This user is not registered")
        db.close()
        await message.answer(
        "Вы не зарегестрировали ни одного устройства с этого аккаунта!"
        )
        return
    user_id=db_user.id
    db_devices = crud.get_device_by_user(db,user_id=user_id)
    db.close()
    d_names=[]
    d_ids=[]
    message_text="Ваши устройства:\n"
    for device in db_devices:
        message_text+=f"{device.device_name} {device.unique_hash}\n"
    db.close()
    logger.info(f"List of devices of user {db_user.name} was returned")
    await message.answer(
        message_text
    )

@dp.message(Command('get_data_from_device'))
async def get_data_from_device(
        message: Message,
        command: CommandObject
):
    # Если не переданы никакие аргументы, то
    # command.args будет None
    logger = get_logger("get_data_device")
    db=SessionLocal()
    db_user=crud.get_users_by_chat_id(db,chat_id=str(message.chat.id))
    if not(db_user):
        logger.error("This user is not registered")
        db.close()
        await message.answer(
        "Вы не зарегестрировали ни одного устройства с этого аккаунта!"
        )
        return
    user_id=db_user.id
    db_devices = crud.get_device_by_user(db,user_id=user_id)
    db.close()
    d_names=[]
    d_ids=[]
    for device in db_devices:
        d_names.append(device.device_name)
        d_ids.append(device.id)
    db.close()
    logger.info(f"List of devices of user {db_user.name} was returned")
    await message.answer(
        "Выберите девайс",reply_markup=get_keyboard_devices_get(device_names=d_names,device_ids=d_ids)
    )

@dp.message(Command('update_data_on_device'))
async def update_data_on_device(
        message: Message,
        command: CommandObject
):
    # Если не переданы никакие аргументы, то
    # command.args будет None
    logger = get_logger("update_data_on_device")
    db=SessionLocal()
    db_user=crud.get_users_by_chat_id(db,chat_id=str(message.chat.id))
    if not(db_user):
        logger.error("This user is not registered")
        db.close()
        await message.answer(
        "Вы не зарегестрировали ни одного устройства с этого аккаунта!"
        )
        return
    user_id=db_user.id
    db_devices = crud.get_device_by_user(db,user_id=user_id)
    d_names=[]
    d_ids=[]
    for device in db_devices:
        d_names.append(device.device_name)
        d_ids.append(device.id)
    db.close()
    logger.info(f"List of devices of user {db_user.name} was returned")
    await message.answer(
        "Выберите девайс",reply_markup=get_keyboard_devices_update(device_names=d_names,device_ids=d_ids)
    )

@dp.callback_query(F.data.startswith("get_device_"))
async def data_return(callback: CallbackQuery):
    device_id = callback.data.split("_")[2]
    print(device_id)
    db=SessionLocal()
    db_device = crud.get_device_by_id(db,device_id=device_id)
    db_device_data = crud.get_data_by_device_id(db,device_id,1)[0]
    logger = get_logger("get_data_device")
    logger.info(f"Info of device {db_device.device_name} was returned")
    db.close()
    await callback.message.answer(
        f"Девайс {db_device.device_name}\n"
        f"Мутность: {db_device_data.turbidity}\n"
        f"Уровень воды: {db_device_data.waterlevel}\n"
        f"Последний ответ:  {db_device_data.created}"
    )
    return

@dp.callback_query(F.data.startswith("update_device_"))
async def data_return(callback: CallbackQuery):
    device_id = callback.data.split("_")[2]
    print(device_id)
    db=SessionLocal()
    db_device = crud.get_device_by_id(db,device_id=device_id)
    logger = get_logger("update_data_device")
    logger.info(f"Info of device {db_device.device_name} was returned")
    db.close()
    client.connect("broker.emqx.io")
    client.loop_start()
    client.publish(f"/pech/esplamp/{db_device.unique_hash}", f"sensors")
    client.disconnect()
    client.loop_stop()
    await callback.message.answer(
        f"На девайс {db_device.device_name} был отправлен запрос на обновление данных. Подождите от 1 до 3 минут и проверьте новые показания через команду get_device_from_data"
    )
    return

@dp.message(Command('configure'))
async def configure_device(
        message: Message,
        command: CommandObject
):
    # Если не переданы никакие аргументы, то
    # command.args будет None
    logger = get_logger("configure_device")
    if command.args is None:
        logger.error("Wrong command format")
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    # Пробуем разделить аргументы на две части по первому встречному пробелу
    try:
        name, time_interval = command.args.split(" ", maxsplit=1)
    # Если получилось меньше двух частей, вылетит ValueError
    except ValueError:
        logger.error(f"parametres of command from {message.from_user.full_name} not found")
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/configure <name> <time>"
        )
        return
    
    db=SessionLocal()
    db_user=crud.get_users_by_chat_id(db,chat_id=str(message.chat.id))
    db_devices=crud.get_device_by_user(db,user_id=db_user.id)
    message_text= ""
    for device in db_devices:
        if device.device_name==name:
            crud.update_feed_interval(db,device_id=device.id,feed_interval=time_interval)
            message_text+=f"Девайс обновлен!\n Имя: {device.device_name}\n Интервал: {time_interval}\n\n"
            print(f"/pech/esplamp/{device.unique_hash}")
            client.connect("broker.emqx.io")
            client.loop_start()
            client.publish(f"/pech/esplamp/{device.unique_hash}", f"feed {device.feed_interval}")
            client.disconnect()
            client.loop_stop()
    db.close()
    
    if len(message_text)==0:
        logger.info(f"Device {name} not found")
        await message.answer(
        f"Девайс {name} не найден"
        )
    else:
        logger.info(f"Config was updated for device {name} ")
        await message.answer(
            message_text
        )


@dp.message(Command('get_data_from_all_devices'))
async def get_data_from_all_devices(
        message: Message,
        command: CommandObject
):
    # Если не переданы никакие аргументы, то
    # command.args будет None
    logger = get_logger("get_data_device")
    db=SessionLocal()
    db_user=crud.get_users_by_chat_id(db,chat_id=str(message.chat.id))
    if not(db_user):
        logger.error("Entered user isnt registered")
        db.close()
        await message.answer(
        "Вы не зарегестрировали ни одного устройства с этого аккаунта!"
        )
        return
    user_id=db_user.id
    db_devices = crud.get_device_by_user(db,user_id=user_id)
    message_text=""
    for device in db_devices:
        message_text+=f"Девайс {device.device_name}\n  Мутность: {device.data[-1].turbidity}\n  Уровень воды: {device.data[-1].waterlevel}\n Последний ответ:  {device.data[-1].created}\n\n"
    db.close()
    logger.info(f"Device info was returned for user {db_user.name} ")
    await message.answer(
        message_text
    )

@dp.message(Command('update_data_on_all_devices'))
async def get_data_from_all_devices(
        message: Message,
        command: CommandObject
):
    # Если не переданы никакие аргументы, то
    # command.args будет None
    logger = get_logger("update_data_device")
    db=SessionLocal()
    db_user=crud.get_users_by_chat_id(db,chat_id=str(message.chat.id))
    if not(db_user):
        logger.error("Entered user isnt registered")
        db.close()
        await message.answer(
        "Вы не зарегестрировали ни одного устройства с этого аккаунта!"
        )
        return
    user_id=db_user.id
    db_devices = crud.get_device_by_user(db,user_id=user_id)
    message_text=""
    for device in db_devices:
        client.connect("broker.emqx.io")
        client.loop_start()
        client.publish(f"/pech/esplamp/{device.unique_hash}", f"sensors")
        client.disconnect()
        client.loop_stop()
        message_text+=f"На девайс {device.device_name} был отправлен запрос на обновление данных.\n"

    db.close()
    logger.info(f"Device info was updated for user {db_user.name} ")
    await message.answer(
        message_text
    )

# Запуск процесса поллинга новых апдейтов
async def start_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())