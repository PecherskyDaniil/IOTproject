from pydantic import BaseModel
import datetime
class DeviceBase(BaseModel):
    device_name:str
    unique_hash:str
    user_id:int


class DeviceCreate(DeviceBase):
    pass


class Device(DeviceBase):
    id: int
    #last_turbidity:float
    #last_waterlevel:float
    last_changed:datetime.datetime
    feed_interval:int
    class Config:
        from_attributes = True
        arbitrary_types_allowed=True

class DeviceDataBase(BaseModel):
    device_id:int
    turbidity:float
    waterlevel:float

class DeviceDataCreate(DeviceDataBase):
    pass

class DeviceData(DeviceDataCreate):
    id: int
    created:datetime.datetime
    class Config:
        from_attributes = True
        arbitrary_types_allowed=True