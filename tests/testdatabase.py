from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from ..DB.database import Base
from ..DB.users import models as usersmodels
from ..DB.users import schemas as usersschemas
from ..DB.devices import models as devicesmodels
from ..DB.devices import schemas as devicesschemas
from logging.handlers import TimedRotatingFileHandler

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Base.metadata.create_all(bind=engine)
usersmodels.Base.metadata.create_all(bind=engine)
devicesmodels.Base.metadata.create_all(bind=engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)