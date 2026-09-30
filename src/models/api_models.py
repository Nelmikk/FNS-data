from pydantic import BaseModel, ConfigDict
from datetime import datetime


class fns_main_info(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inn: str
    ogrn: str
    main_okved_name: str | None = None
    main_okved_code: str | None = None
    full_name: str | None = None
    short_name: str | None = None
    subject_type: str | None = None
    subject_category: str | None = None
    inclusion_date: datetime | None = None
    is_social: str | None = None
    avg_employees_num: int | None = None
    region_code: str | None = None
    region: str | None = None
    district: str | None = None
    area: str | None = None


class sno(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inn: str
    ogrn: str

    eshn: bool
    usn: bool
    ausn: bool
    srp: bool
    psn: bool
    npd: bool


class ADDITIONAL_OKVEDS_DATA(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str | None = None
    name: str | None = None

class okveds(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inn: str
    ogrn: str
    additional_okveds_data: list[ADDITIONAL_OKVEDS_DATA]


class LICENSES_DATA(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    num: str | None = None
    date: str | None = None
    date_start: datetime | None = None
    date_end: datetime | None = None

class licenses(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inn: str
    ogrn: str
    licenses_data: list[LICENSES_DATA]


class full_data(BaseModel):
    inn: str
    ogrn: str
    main_okved_name: str | None = None
    main_okved_code: str | None = None
    full_name: str | None = None
    short_name: str | None = None
    subject_type: str | None = None
    subject_category: str | None = None
    inclusion_date: datetime | None = None
    is_social: str | None = None
    avg_employees_num: int | None = None
    region_code: str | None = None
    region: str | None = None
    district: str | None = None
    area: str | None = None

    eshn: bool | None = None
    usn: bool | None = None
    ausn: bool | None = None
    srp: bool | None = None
    psn: bool | None = None
    npd: bool | None = None

    additional_okveds_data: list[ADDITIONAL_OKVEDS_DATA] | None = list()

    licenses_data: list[LICENSES_DATA] | None = list()


__all__ = ['full_data', 'licenses', 'okveds', 'sno', 'fns_main_info']