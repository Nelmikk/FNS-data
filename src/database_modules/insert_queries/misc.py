from functools import wraps
from typing import Callable
from inspect import iscoroutinefunction


def batch_data(batch_size: int = 16_000, ):
    """
    Разделение больших запросов на меньшие запросы.
    :param batch_size:  Размер строк в запросе.
    :return:
    """
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

        @wraps(func)
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

        if iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return batch