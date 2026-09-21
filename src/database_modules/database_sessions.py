from typing import Callable, Coroutine
from functools import wraps

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from src.database_modules.database_conf import settings_super_user

def batch_data(batch_size: int = 16_000, ):
    def batch(func: Callable, ):
        @wraps(func)
        async def async_wrapper(*args, **kwargs, ):
            nonlocal batch_size
            rows_num = len(kwargs['values'])
            step = int(batch_size / (len(kwargs['values'][0])))  # Оптимизация батчей

            for left in range(0, rows_num, step):
                if left + step > rows_num:
                    await func(*args,
                               tablename=kwargs['tablename'],
                               values=kwargs['values'][left:rows_num + 1],
                               engine=kwargs['engine'], )
                else:
                    await func(*args,
                               tablename=kwargs['tablename'],
                               values=kwargs['values'][left:left + step],
                               engine=kwargs['engine'], )
                return

        def sync_wrapper(*args, **kwargs, ):
            nonlocal batch_size
            rows_num = len(kwargs['values'])
            step = int(batch_size / (len(kwargs['values'][0])))  # Оптимизация батчей

            for left in range(0, rows_num, step):
                if left + step > rows_num:
                    func(*args,
                               tablename=kwargs['tablename'],
                               values=kwargs['values'][left:rows_num + 1],
                               engine=kwargs['engine'], )
                else:
                    func(*args,
                               tablename=kwargs['tablename'],
                               values=kwargs['values'][left:left + step],
                               engine=kwargs['engine'], )
                return

        if isinstance(func, Coroutine): return async_wrapper
        else: return sync_wrapper
    return batch



async_engine = create_async_engine(url=settings_super_user.DATABASE_URL_ASYNC)
sync_engine = create_engine(url=settings_super_user.DATABASE_URL)

async_session = async_sessionmaker(async_engine)
sync_session = sessionmaker(sync_engine)
