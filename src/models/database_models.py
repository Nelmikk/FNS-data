from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import inspect, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from typing import TypedDict

from datetime import datetime


class Base_index(TypedDict):
    index_name: str
    column_index: str
    index_type: str


class Base(DeclarativeBase):
    _indexes: list[Base_index]
    __nonshadow_tablename__: str
    ...


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


class fns_main_info_mixin:
    id: Mapped[int] = mapped_column(BigInteger,
                                    primary_key=True,
                                    autoincrement=True)
    inn: Mapped[int] = mapped_column(BigInteger, )
    ogrn: Mapped[int] = mapped_column(BigInteger, )
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

    _indexes = [Base_index(index_name='inn_index', column_index='inn', index_type='hash'),
                Base_index(index_name='ogrn_index', column_index='ogrn', index_type='hash')]

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


class fns_main_info_shadow(fns_main_info_mixin, Base):
    __tablename__ = 'fns_main_info_shadow'
    __nonshadow_tablename__ = fns_main_info.__tablename__


class sno_mixin:
    id: Mapped[int] = mapped_column(BigInteger,
                                    primary_key=True,
                                    autoincrement=True, )
    inn: Mapped[int] = mapped_column(BigInteger,
                                     nullable=False, )
    eshn: Mapped[bool]
    usn: Mapped[bool]
    ausn: Mapped[bool]
    srp: Mapped[bool]
    psn: Mapped[bool]
    npd: Mapped[bool]

    _indexes = [Base_index(index_name='inn_index', column_index='inn', index_type='hash'), ]


class sno(sno_mixin, Base):
    __tablename__ = 'sno'


class sno_shadow(sno_mixin, Base):
    __tablename__ = 'sno_shadow'
    __nonshadow_tablename__ = sno.__tablename__


class okveds_mixin:
    id: Mapped[int] = mapped_column(BigInteger,
                                    primary_key=True,
                                    autoincrement=True, )
    inn: Mapped[int] = mapped_column(BigInteger,
                                     nullable=False, )
    ogrn: Mapped[int] = mapped_column(BigInteger,
                                      nullable=False, )
    # name: Mapped[str]
    code: Mapped[str]

    _indexes = [Base_index(index_name='inn_index', column_index='inn', index_type='hash')]

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


class okveds_shadow(okveds_mixin, Base):
    __tablename__ = 'okveds_shadow'
    __nonshadow_tablename__ = okveds.__tablename__


class relevant_okveds_mixin:
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


class relevant_okveds(relevant_okveds_mixin, Base):
    __tablename__ = 'relevant_okveds'


class relevant_okveds_shadow(relevant_okveds_mixin, Base):
    __tablename__ = 'relevant_okveds_shadow'
    __nonshadow_tablename__ = relevant_okveds.__tablename__



class licenses_mixin:
    id: Mapped[int] = mapped_column(BigInteger,
                               primary_key=True,
                               autoincrement=True)
    inn: Mapped[int] = mapped_column(BigInteger)
    ogrn: Mapped[int] = mapped_column(BigInteger)
    num: Mapped[str]
    date: Mapped[datetime | None]
    date_start: Mapped[datetime | None]
    date_end: Mapped[datetime | None]

    _indexes = [Base_index(index_name='inn_index', column_index='inn', index_type='hash')]


class licenses(licenses_mixin, Base):
    __tablename__ = 'licenses'


class licenses_shadow(licenses_mixin, Base):
    __tablename__ = 'licenses_shadow'
    __nonshadow_tablename__ = licenses.__tablename__



models_dict = {x.__name__: x for x in Base.__subclasses__()}
models_primary_keys_dict = {x.__name__: [inspect(x).primary_key[0].key]
                            for x in Base.__subclasses__() if inspect(x).primary_key}    # Словарь из первых первичных ключей в таблице