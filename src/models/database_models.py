from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import inspect, BigInteger, VARCHAR
from sqlalchemy.dialects.postgresql import JSONB

from typing import TypedDict, Any

from datetime import datetime


class SNO_DATA(TypedDict):
    eshn: bool
    usn: bool
    ausn: bool
    srp: bool
    psn: bool
    npd: bool


class ADDITIONAL_OKVEDS_DATA(TypedDict):
    code: str
    name: str


class LICENSES_DATA(TypedDict):
    num: str | None
    date: str | None
    date_start: datetime | None
    date_end: datetime | None


class Base_index(TypedDict):
    index_name: str
    column_index: str
    index_type: str


class Base(DeclarativeBase):
    DB_indexes: tuple[Base_index] = tuple()
    ...

class Base_shadow_table:
    """
    Добавляется для моделей shadow таблиц.
    """
    non_shadow_table: type[Base]

# class kadarbitr_cases(Base):
#     __tablename__ = 'kadarbitr_cases'
#     # id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     case_num: Mapped[str] = mapped_column(primary_key=True)
#     case_link: Mapped[str]
#     case_date: Mapped[datetime]
#     case_type: Mapped[str]
#     court: Mapped[str]
#     judge: Mapped[str]
#     case_status: Mapped[str] = mapped_column(nullable=True)
#     last_doc_name: Mapped[str] = mapped_column(nullable=True)
#
#
# class kadarbitr_plaintiffs(Base):
#     __tablename__ = 'kadarbitr_plaintiffs'
#     id: Mapped[int] = mapped_column(primary_key=True,
#                                     autoincrement=True)
#     case_num: Mapped[str]
#     inn: Mapped[int] = mapped_column(BigInteger)
#     name: Mapped[str]
#     info: Mapped[str]
#
#
# class kadarbitr_respondents(Base):
#     __tablename__ = 'kadarbitr_respondents'
#     id: Mapped[int] = mapped_column(primary_key=True,
#                                     autoincrement=True)
#     case_num: Mapped[str]
#     inn: Mapped[int]
#     name: Mapped[str]
#     info: Mapped[str]


class Base_mixin:
    base_column_values: dict[str, Any]


class fns_main_info_mixin(Base_mixin):
    id: Mapped[int] = mapped_column(BigInteger,
                                    primary_key=True,
                                    autoincrement=True)
    inn: Mapped[str] = mapped_column(VARCHAR(12))
    ogrn: Mapped[str] = mapped_column(VARCHAR(15))
    main_okved_name: Mapped[str] = mapped_column(nullable=True)
    main_okved_code: Mapped[str] = mapped_column(nullable=True)
    full_name: Mapped[str] = mapped_column(nullable=True)
    short_name: Mapped[str] = mapped_column(nullable=True)
    subject_type: Mapped[str] = mapped_column(nullable=True)
    subject_category: Mapped[str] = mapped_column(nullable=True)
    inclusion_date: Mapped[datetime] = mapped_column(nullable=True)
    is_social: Mapped[str] = mapped_column(nullable=True)
    avg_employees_num: Mapped[int] = mapped_column(nullable=True)
    region_code: Mapped[str] = mapped_column(nullable=True)
    region: Mapped[str] = mapped_column(nullable=True)
    district: Mapped[str] = mapped_column(nullable=True)
    area: Mapped[str] = mapped_column(nullable=True)

    base_column_values = {
    'inn': None,
    'ogrn': None,
    'main_okved_name': None,
    'main_okved_code': None,
    'full_name': None,
    'short_name': None,
    'subject_type': None,
    'subject_category': None,
    'inclusion_date': None,
    'is_social': None,
    'avg_employees_num': None,
    'region_code': None,
    'region': None,
    'district': None,
    'area': None,
    }

    # __table_args__ = (
    #     Index('index_inn_main_info',
    #           'inn',
    #           postgresql_using='hash'),         # Хэш индекс, тк частое обращения по конкретному ИНН
    #     Index('index_ogrn_main_info',
    #           'ogrn',
    #           postgresql_using='hash'),         # Хэш индекс, тк частое обращения по конкретному ОГРН
    # )


class fns_main_info(fns_main_info_mixin, Base):
    __tablename__ = 'fns_main_info'

    DB_indexes = [Base_index(index_name=f'inn_index_fns_main_info', column_index='inn', index_type='btree'),
                  Base_index(index_name='ogrn_index_fns_main_info', column_index='ogrn', index_type='btree')]


class fns_main_info_shadow(fns_main_info_mixin, Base, Base_shadow_table):
    __tablename__ = 'fns_main_info_shadow'
    non_shadow_table = fns_main_info
    DB_indexes = [Base_index(index_name=f'inn_index_fns_main_info_shadow', column_index='inn', index_type='btree'),
                  Base_index(index_name='ogrn_index_fns_main_info_shadow', column_index='ogrn', index_type='btree')]


class sno_mixin(Base_mixin):
    id: Mapped[int] = mapped_column(BigInteger,
                                    primary_key=True,
                                    autoincrement=True, )
    inn: Mapped[str] = mapped_column(VARCHAR(12),
                                     nullable=False)
    ogrn: Mapped[str] = mapped_column(VARCHAR(15),
                                      nullable=True)
    eshn: Mapped[bool]
    usn: Mapped[bool]
    ausn: Mapped[bool]
    srp: Mapped[bool]
    psn: Mapped[bool]
    npd: Mapped[bool]

    base_column_values = {
        'inn': None,
        'ogrn': None,
        'eshn': False,
        'usn': False,
        'ausn': False,
        'srp': False,
        'psn': False,
        'npd': False,
    }

    # _indexes = [Base_index(index_name='inn_index', column_index='inn', index_type='hash'), ]


class sno(sno_mixin, Base):
    __tablename__ = 'sno'
    DB_indexes = [Base_index(index_name=f'inn_index_fns_sno', column_index='inn', index_type='btree'), ]


class sno_shadow(sno_mixin, Base, Base_shadow_table):
    __tablename__ = 'sno_shadow'
    non_shadow_table = sno

    DB_indexes = [Base_index(index_name=f'inn_index_fns_sno_shadow', column_index='inn', index_type='btree'), ]


class okveds_mixin(Base_mixin):
    id: Mapped[int] = mapped_column(BigInteger,
                                    primary_key=True,
                                    autoincrement=True, )
    inn: Mapped[str] = mapped_column(VARCHAR(12),
                                     nullable=False, )
    ogrn: Mapped[str] = mapped_column(VARCHAR(15),
                                      nullable=False, )
    additional_okveds_data: Mapped[list[ADDITIONAL_OKVEDS_DATA]] = mapped_column(JSONB)

    base_column_values = {
        'inn': None,
        'ogrn': None,
        'additional_okveds_data': [],
    }
    # name: Mapped[str]
    # code: Mapped[str]

    # _indexes = [Base_index(index_name='inn_index', column_index='inn', index_type='hash')]

    # __table_args__ = (
    #     Index('index_inn_okveds',
    #           'inn',
    #           postgresql_using='hash'),
    #     Index('index_ogrn_okveds',
    #           'ogrn',
    #           postgresql_using='hash')
    # )


class okveds(okveds_mixin, Base):
    __tablename__ = 'okveds'
    DB_indexes = [Base_index(index_name=f'inn_index_okveds', column_index='inn', index_type='btree'), ]


class okveds_shadow(okveds_mixin, Base, Base_shadow_table):
    __tablename__ = 'okveds_shadow'
    non_shadow_table = okveds
    DB_indexes = [Base_index(index_name=f'inn_index_okveds_shadow', column_index='inn', index_type='btree'), ]



class relevant_okveds_mixin(Base_mixin):
    """
    Плейсхолдер, если потребуется и эту таблицу перемещать через алембик.
    """
    # id: Mapped[int] = mapped_column(BigInteger,
    #                                 primary_key=True,
    #                                 autoincrement=True, )
    letter: Mapped[str]
    code: Mapped[str] = mapped_column(unique=True,
                                      primary_key=True,
                                      autoincrement=False)
    name: Mapped[str]
    base_column_values = {
        'letter': None,
        'code': None,
        'name': None,
    }


class relevant_okveds(relevant_okveds_mixin, Base):
    __tablename__ = 'relevant_okveds'


class relevant_okveds_shadow(relevant_okveds_mixin, Base, Base_shadow_table):
    __tablename__ = 'relevant_okveds_shadow'
    non_shadow_table = relevant_okveds



class licenses_mixin(Base_mixin):
    id: Mapped[int] = mapped_column(BigInteger,
                               primary_key=True,
                               autoincrement=True)
    inn: Mapped[str] = mapped_column(VARCHAR(12))
    ogrn: Mapped[str] = mapped_column(VARCHAR(15))
    licenses_data: Mapped[list[LICENSES_DATA]] = mapped_column(JSONB)

    # num: Mapped[str]
    # date: Mapped[datetime | None]
    # date_start: Mapped[datetime | None]
    # date_end: Mapped[datetime | None]

    # _indexes = [Base_index(index_name='inn_index', column_index='inn', index_type='hash')]


class licenses(licenses_mixin, Base):
    __tablename__ = 'licenses'
    DB_indexes = [Base_index(index_name=f'inn_index_licenses', column_index='inn', index_type='btree'), ]


class licenses_shadow(licenses_mixin, Base, Base_shadow_table):
    __tablename__ = 'licenses_shadow'
    non_shadow_table = licenses
    DB_indexes = [Base_index(index_name=f'inn_index_licenses_shadow', column_index='inn', index_type='btree'), ]



models_dict = {x.__name__: x for x in Base.__subclasses__()}
models_primary_keys_dict = {x.__name__: [inspect(x).primary_key[0].key]
                            for x in Base.__subclasses__() if inspect(x).primary_key}    # Словарь из первых первичных ключей в таблице