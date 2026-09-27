from typing import Callable, AsyncGenerator, TypedDict
from functools import wraps
from inspect import iscoroutinefunction
from sqlalchemy.engine import CursorResult
from sqlalchemy import TextClause


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




async def fetch_result(results: CursorResult, ) -> AsyncGenerator:
    keys = results.keys()._keys
    for result in results.fetchall():
        print(result)
        yield {k: v for k, v in zip(keys, result) if k != 'id'}
    ...


async def divide_output(results: CursorResult, ) -> AsyncGenerator:
    keys = results.keys()
    ogrn = 0
    output = None

    for result in results.fetchall():

        row = {k: v for k, v in zip(keys, result) if k != 'id'}
        if row['ogrn'] != ogrn:

            if ogrn:
                response, output = output, None
                yield response

            ogrn = row['ogrn']
            output = {'inn': row['inn'], 'ogrn': row['ogrn'], 'data': []}
            output['data'].append({k: v for k, v in row.items() if k not in ['inn', 'ogrn']})

        else:
            output['data'].append({k: v for k, v in row.items() if k not in ['inn', 'ogrn']})
    yield output


class SELECT_QUERY(TypedDict):
    statement: TextClause
    parameters: dict[str, str]