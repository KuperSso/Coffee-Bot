import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncAttrs, create_async_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()
DATABASE_URL = os.getenv("database_url")
engine = create_async_engine(DATABASE_URL)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass
