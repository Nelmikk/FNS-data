from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from src.database_modules.database_conf import settings_super_user



async_engine = create_async_engine(url=settings_super_user.DATABASE_URL_ASYNC)
sync_engine = create_engine(url=settings_super_user.DATABASE_URL)

async_session = async_sessionmaker(async_engine)
sync_session = sessionmaker(sync_engine)
