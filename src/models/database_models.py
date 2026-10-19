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


class Base_shadow_table:
    """
    Добавляется для моделей shadow таблиц.
    """
    non_shadow_table: type[Base]


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
    is_social: Mapped[bool] = mapped_column(nullable=True)
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


class fns_main_info(fns_main_info_mixin, Base):
    __tablename__ = 'fns_main_info'

    DB_indexes = [Base_index(index_name=f'inn_index_fns_main_info', column_index='inn', index_type='btree'),
                  Base_index(index_name='ogrn_index_fns_main_info', column_index='ogrn', index_type='btree')
                  ]


class fns_main_info_shadow(fns_main_info_mixin, Base, Base_shadow_table):
    __tablename__ = 'fns_main_info_shadow'
    non_shadow_table = fns_main_info
    DB_indexes = [Base_index(index_name=f'inn_index_fns_main_info_shadow', column_index='inn', index_type='btree'),
                  Base_index(index_name='ogrn_index_fns_main_info_shadow', column_index='ogrn', index_type='btree')
                  ]


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


class sno(sno_mixin, Base):
    __tablename__ = 'sno'
    DB_indexes = [Base_index(index_name='inn_index_fns_sno', column_index='inn', index_type='btree'),
                  Base_index(index_name='ogrn_index_fns_sno', column_index='ogrn', index_type='btree')
                  ]


class sno_shadow(sno_mixin, Base, Base_shadow_table):
    __tablename__ = 'sno_shadow'
    non_shadow_table = sno

    DB_indexes = [Base_index(index_name='inn_index_fns_sno_shadow', column_index='inn', index_type='btree'),
                  Base_index(index_name='ogrn_index_fns_sno_shadow', column_index='ogrn', index_type='btree')
                  ]


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


class okveds(okveds_mixin, Base):
    __tablename__ = 'okveds'
    DB_indexes = [Base_index(index_name='inn_index_okveds', column_index='inn', index_type='btree'),
                  Base_index(index_name='ogrn_index_okveds', column_index='ogrn', index_type='btree')]


class okveds_shadow(okveds_mixin, Base, Base_shadow_table):
    __tablename__ = 'okveds_shadow'
    non_shadow_table = okveds
    DB_indexes = [Base_index(index_name='inn_index_okveds_shadow', column_index='inn', index_type='btree'),
                  Base_index(index_name='ogrn_index_okveds_shadow', column_index='ogrn', index_type='btree')]



class licenses_mixin(Base_mixin):
    id: Mapped[int] = mapped_column(BigInteger,
                               primary_key=True,
                               autoincrement=True)
    inn: Mapped[str] = mapped_column(VARCHAR(12))
    ogrn: Mapped[str] = mapped_column(VARCHAR(15))
    licenses_data: Mapped[list[LICENSES_DATA]] = mapped_column(JSONB)

    base_column_values = {
        'inn': None,
        'ogrn': None,
        'licenses_data': [],
    }


class licenses(licenses_mixin, Base):
    __tablename__ = 'licenses'
    DB_indexes = [Base_index(index_name=f'inn_index_licenses', column_index='inn', index_type='btree'),
                  Base_index(index_name=f'ogrn_index_licenses', column_index='ogrn', index_type='btree'),
                  ]


class licenses_shadow(licenses_mixin, Base, Base_shadow_table):
    __tablename__ = 'licenses_shadow'
    non_shadow_table = licenses
    DB_indexes = [Base_index(index_name=f'inn_index_licenses_shadow', column_index='inn', index_type='btree'),
                  Base_index(index_name=f'ogrn_index_licenses_shadow', column_index='ogrn', index_type='btree'),
                  ]



models_dict = {x.__name__: x for x in Base.__subclasses__()}
models_primary_keys_dict = {x.__name__: [inspect(x).primary_key[0].key]
                            for x in Base.__subclasses__() if inspect(x).primary_key}    # Словарь из первых первичных ключей в таблице