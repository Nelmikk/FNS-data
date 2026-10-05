from typing import Callable

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine

from src.database_modules.database_conf import settings_super_user, settings_select_user

def check_for_url_param(func: Callable, ):
    def wrapper(**kwargs, ):
        if 'url' in kwargs.keys():
            kwargs.pop('url')
        return func(**kwargs)
    return wrapper


@check_for_url_param
def get_async_engine_super_user(**kwargs, ) -> AsyncEngine:
    return create_async_engine(url=settings_super_user.DATABASE_URL_ASYNC, **kwargs)

@check_for_url_param
def get_sync_engine_super_user(**kwargs, ) -> Engine:
    return create_engine(url=settings_super_user.DATABASE_URL, **kwargs)

@check_for_url_param
def get_async_engine_select_user(**kwargs, ) -> AsyncEngine:
    return create_async_engine(url=settings_select_user.DATABASE_URL, **kwargs)

@check_for_url_param
def get_sync_engine_select_user(**kwargs, ) -> Engine:
        return create_engine(url=settings_select_user.DATABASE_URL, **kwargs)

@check_for_url_param
def get_async_sessionmaker(async_engine: AsyncEngine, **kwargs,) -> async_sessionmaker:
        return async_sessionmaker(async_engine, **kwargs)

@check_for_url_param
def get_sessionmaker(sync_engine, **kwargs, ) -> sessionmaker:
        return sessionmaker(sync_engine, **kwargs)



# async_engine = create_async_engine(url=settings_super_user.DATABASE_URL_ASYNC)
# sync_engine = create_engine(url=settings_super_user.DATABASE_URL)
#
# async_engine_select_user = create_async_engine(url=settings_select_user.DATABASE_URL_ASYNC)
# sync_engine_select_user = create_engine(url=settings_select_user.DATABASE_URL)

# async_session = async_sessionmaker(async_engine)
# sync_session = sessionmaker(sync_engine)
#
# async_session_select_user = async_sessionmaker(async_engine_select_user)
# sync_session_select_user = sessionmaker(sync_engine_select_user)
