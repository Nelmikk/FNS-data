from src.models.database_models import Base


class FNS_DATA:
    ...


def create_dict_from_database_model(database_model: type[Base], ) -> dict | None:
    """
    Конуструктор словарей для хранения данных при парсинге.
    Словарь генерируется из столбцов БД модели.
    Если модель не объявлена, возвращает None.

        Возвращает словарь вида:
                {
                    col1_name: val1,
                    col2_name: val2,
                    ...
                }

        Юзается след образом:
            var = create_dict_from_database_model(_database_model: type[Base] = database_model_class)

    :param database_model:
    :return dict | None:
    """
    try: return {k.name: False if k.type.python_type is bool else None
                 for k in database_model.__table__.columns if k.name != 'id'}
    except: return None


def get_tablename_from_database_model(database_model: type[Base], ) -> str | None:
    """
    Возвращает название таблицы в БД из модели БД, созданной в /src/models/database_models.py.
    Если модель не объявлена, возвращает None.

        Юзается след образом:
            table_name = get_tablename_from_database_model(_database_model: type[Base] = database_model_class)

    :param database_model:
    :return str | None:
    """
    try: return database_model.__tablename__
    except: return None
    ...

# dict_from_database_model_name = {table.__tablename__:
#                                      {column.name: False if column.type.python_type is bool else None for column in table.__table__.columns if column.name != 'id'}
#                                  for table in Base.__subclasses__()}
#
# tablename_from_database_model_name = {table.__name__: table.__tablename__ for table in Base.__subclasses__()}

# @dataclass
# class ORG_MAIN_INFO(FNS_DATA):
#     table: str = 'fns_main_info_shadow' # Добавить импорт откуда-то для общего названия таблицы
#
#     inclusion_date: datetime.date | None = None  # Дата включения в реестр МСП                                      ДатаВклМСП
#     subject_type: str | None  = None             # Тип субъекта (Юр лицо/ИП/тд)                                     ВидСубМСП
#     subject_category: str | None = None          # Категория субъекта (Микро/малое/среднее предприятие)             КатСубМСП
#     is_social: str | None = None                 # Является ли субъект социальным предприятием                      СведСоцПред
#
#     avg_employees_num: int | None = None         # Среднесписочная численность работников                           ССЧР
#     inn: int | None = None                       # ИНН                                                              ИННЮЛ/ИННФЛ
#     ogrn: int | None = None                      # ОГРН                                                             ОГРН/ОГРНИП
#     full_name: str | None  = None                # ФИО ИП/Полное название организации                               ФИОИП
#     short_name: str | None = None                # Сокращенное название организации                                 НаимОргСокр
#
#     region_code: str | None = None               # Код региона                                                      КодРегион
#     region: str | None = None                    # Субъект РФ                                                       Регион
#     district: str | None = None                  # Район                                                            Район
#     area: str | None = None                      # Населенный пункт                                                 НаселПункт
#
#     # Сведения об основном ОКВЭДе                                      СвОКВЭДОсн
#     main_okved_code: str | None = None           # Код ОКВЭДа                                                       КодОКВЭД
#     main_okved_name: str | None = None           # Наименование ОКВЭДа                                              НаимОКВЭД
#
#
# @dataclass
# class ORG_ADDITIONAL_OKVEDS(FNS_DATA):
#     table: str = 'okveds_shadow' # Добавить импорт откуда-то для общего названия таблицы
#
#     inn: int | None = None
#     ogrn: int | None = None
#     name: str | None = None
#     code: str | None = None
#
#
#
# @dataclass
# class ORG_SNO(FNS_DATA):
#     table: str = 'sno_shadow' # Добавить импорт откуда-то для общего названия таблицы
#
#     inn: int | None = None
#     eshn: bool | None = False
#     usn: bool | None = False
#     ausn: bool | None = False
#     srp: bool | None = False
#     psn: bool | None = False
#     npd: bool | None = False


