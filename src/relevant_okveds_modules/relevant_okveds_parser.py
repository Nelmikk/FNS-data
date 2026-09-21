from typing import Any

from src.models.other_models import get_tablename_from_database_model
from src.models.database_models import relevant_okveds_shadow


class Parser_relevant_okveds:
    def __init__(self, ):
        self._database_model = relevant_okveds_shadow


    def parse(self, xlsx_file_data: str) -> dict[str, str | None | list[Any]]:
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

        :return:
        """
        tablename = get_tablename_from_database_model(self._database_model)
        if tablename is None:
            print(f'The tablename was not found using model {self._database_model.__name__}')
        output = {'tablename': tablename, 'data': []}
        try:

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