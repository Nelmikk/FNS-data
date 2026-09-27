from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class fns_main_info(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inn: str
    ogrn: str
    main_okved_name: str | None
    main_okved_code: str | None
    full_name: str | None
    short_name: str | None
    subject_type: str | None
    subject_category: str | None
    inclusion_date: datetime | None
    is_social: str | None
    avg_employees_num: int | None
    region_code: str | None
    region: str | None
    district: str | None
    area: str | None


# class sno_data(BaseModel):
#     model_config = ConfigDict(from_attributes=True)
#
#     eshn: bool
#     usn: bool
#     ausn: bool
#     srp: bool
#     psn: bool
#     npd: bool

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


class okveds_data(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    letter: str
    name: str
    code: str


class okveds(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inn: str
    ogrn: str
    data: list[okveds_data]



class licenses_data(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    num: str | None = None
    date: datetime | None = None
    date_start: datetime | None = None
    date_end: datetime | None = None


class licenses(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inn: str
    ogrn: str
    data: list[licenses_data | None] | None = None


# class full_info(BaseModel):
#     model_config = ConfigDict(from_attributes=True)
#
#     inn: str
#     ogrn: str
#     main_okved_name: str | None
#     main_okved_code: str | None
#     full_name: str | None
#     short_name: str | None
#     subject_type: str | None
#     subject_category: str | None
#     inclusion_date: datetime | None
#     is_social: str | None
#     avg_employees_num: int | None
#     region_code: str | None
#     region: str | None
#     district: str | None
#     area: str | None
#
#     additional_okveds: list[full_info_ovkeds] | None = []

    ...