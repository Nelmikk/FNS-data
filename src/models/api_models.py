from pydantic import BaseModel, ConfigDict
from datetime import datetime


class fns_main_info(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inn: int
    ogrn: int
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


class sno(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    eshn: bool
    usn: bool
    ausn: bool
    srp: bool
    psn: bool
    npd: bool


class okveds(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inn: int
    ogrn: int
    name: str
    code: str


class full_info_ovkeds(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str | None
    name: str | None


class full_info(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inn: int
    ogrn: int
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

    additional_okveds: list[full_info_ovkeds] | None = []

    ...