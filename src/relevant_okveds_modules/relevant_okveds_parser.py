from typing import Any

from src.errors.database_errors import TableNotFound
from src.models.other_models import get_tablename_from_database_model, Parser_output
from src.models.database_models import relevant_okveds_shadow


class Parser_relevant_okveds:
    def __init__(self, ):
        self._database_model = relevant_okveds_shadow


    def parse(self, xlsx_file_data: str) -> Parser_output:
        """
        Возвращает данные всех актуальных ОКВЭДов.

        :return:
        """
        tablename = get_tablename_from_database_model(self._database_model)
        if tablename is None:
            raise TableNotFound
        output = Parser_output(tablename=tablename, data=[])
        try:

            for row in xlsx_file_data.split(sep='\n'):
                row = row.replace('"', '').split(sep=';', maxsplit=2)
                if not all(i for i in row):
                    continue
                letter, code, name = row
                if not code.split():
                    continue
                output['data'].append({'letter': row[0].strip(),
                                       'code': row[1].strip(),
                                       'name': row[2].strip()})

        except:
            print('Error while getting relevant okveds.')

        finally:
            return output