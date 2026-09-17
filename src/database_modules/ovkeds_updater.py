import requests
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from src.database_modules.core import insert_data_async
from src.database_modules.database_conf import settings_super_user
from src.models.other_models import get_tablename_from_database_model
from src.models.database_models import relevant_okveds_shadow


class Updater_okveds:
    def __init__(self, ):
        ...


    async def update_and_insert(self, ) -> None:
        relevant_okveds = self.get_relevant_data()
        if not relevant_okveds['data']:
            return None
        engine = create_async_engine(url=settings_super_user.DATABASE_URL_ASYNC, echo=False, )
        await insert_data_async(tablename=relevant_okveds['tablename'],
                                values=relevant_okveds['data'],
                                engine=engine)



    def get_relevant_data(self, ) -> dict[str, str | list[dict[str, str]]]:
        """
        Скачивает xlsx-файл с https://classifikators.ru, парсит его и возвращает словарь вида:

            {
                'tablename': str,
                'data' :
                [
                    {
                        'letter': str,
                        'code': str,
                        'name': str,
                    },
                ]
            ...
            }

            В словарях буква, код, наименование всех актуальных ОКВЭДов.

            Юзается для занесения данных в БД.

        :return:
        """
        tablename = get_tablename_from_database_model(relevant_okveds_shadow)
        if tablename is None:
            print(f'The tablename was not found using model {relevant_okveds_shadow.__name__}')
        output = {'tablename': tablename, 'data': []}
        try:
            xlsx_file_data = requests.get('https://classifikators.ru/assets/downloads/okved/okved.csv')
            xlsx_file_data = xlsx_file_data.content.decode('utf-8')
            for row in xlsx_file_data.split(sep='\n'):
                row = row.replace('"', '').split(sep=';', maxsplit=2)
                if not all(i for i in row):
                    continue
                letter, code, name = row
                if not code.split():
                    continue
                output['data'].append({'letter': row[0], 'code': row[1], 'name': row[2]})

        except:
            print('Error while getting relevant okveds.')

        finally:
            return output




asyncio.run(Updater_okveds().update_and_insert())