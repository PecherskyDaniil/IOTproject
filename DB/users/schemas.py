from pydantic import BaseModel
from ..devices.models import Device
class UserBase(BaseModel):
    chat_id: str
    name: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    devices:list[Device] = []

    class Config:
        from_attributes = True
        arbitrary_types_allowed=True