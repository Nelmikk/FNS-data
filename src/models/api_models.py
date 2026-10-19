from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class fns_main_info(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inn: str = Field(description='ИНН',
                     examples=['0123456789'])
    ogrn: str = Field(description='ОГРН',
                      examples=['0123456789012'])
    main_okved_name: str | None = Field(default=None,
                                        description='Наименование основново ОКВЭДа',
                                        examples=['Подача напитков'])
    main_okved_code: str | None = Field(default=None,
                                        description='Код основново ОКВЭДа',
                                        examples=['56.30'])
    full_name: str | None = Field(default=None,
                                  description='Полное наименование юридического лица',
                                  examples=['ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "Ромашка"'])
    short_name: str | None = Field(default=None,
                                   description='Сокращенное наименование юридического лица',
                                   examples=['ООО "Ромашка"'])
    subject_type: str | None = Field(default=None,
                                     description='Вид субъекта МСП',
                                     examples=['юридическое лицо'])
    subject_category: str | None = Field(default=None,
                                         description='Категория субъекта МСП',
                                         examples=['микропредприятие'])
    inclusion_date: datetime | None = Field(default=None,
                                            description='Дата включения в реестр МСП',
                                            examples=[datetime.strptime('2025-12-10', '%Y-%m-%d')])
    is_social: bool | None = Field(default=None,
                                   description='Является ли социальным предприятием',
                                   examples=[True])
    region_code: str | None = Field(default=None,
                                    description='Код региона',
                                    examples=['42'])
    region: str | None = Field(default=None,
                               description='Субъект РФ',
                               examples=['обл. Кемеровская область - Кузбасс'])
    district: str | None = Field(default=None,
                                 description='Район',
                                 examples=['р-н Крапивинский'])
    area: str | None = Field(default=None,
                             description='Город',
                             examples=['пгт. Крапивинский'])


class sno(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inn: str = Field(description='ИНН',
                     examples=['0123456789'])
    ogrn: str = Field(description='ОГРН',
                      examples=['0123456789012'])

    eshn: bool = Field(description='Применение СНО в виде единого сельскохозяйственного налога',
                       examples=[True])
    usn: bool = Field(description='Применение упрощенной системы налогообложения',
                      examples=[False])
    ausn: bool = Field(description='Применение автоматизированной упрощенной системы налогообложения',
                       examples=[False])
    srp: bool = Field(description='Применение системы налогообложения при выполнении соглашения о разделе продукции',
                      examples=[False])
    psn: bool = Field(description='Применение патентной системы налогообложения',
                      examples=[False])
    npd: bool = Field(description='Налог на профессиональный доход',
                      examples=[False])


class ADDITIONAL_OKVEDS_DATA(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str | None = Field(default=None,
                             description='')
    name: str | None = Field(default=None,
                             description='')

class okveds(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inn: str = Field(description='ИНН',
                     examples=['0123456789'])
    ogrn: str = Field(description='ОГРН',
                      examples=['0123456789012'])
    additional_okveds_data: list[ADDITIONAL_OKVEDS_DATA]


class LICENSES_DATA(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    num: str | None = Field(default=None,
                            description='Номер лицензии',
                            examples=['ACC-67-067420'])
    date: str | None = Field(default=None,
                             description='Дата лицензии',
                             examples=[datetime.strptime('2018-01-01', '%Y-%m-%d')])
    date_start: datetime | None = Field(default=None,
                                        description='Дата начала действия лицензии',
                                        examples=[datetime.strptime('2018-01-01', '%Y-%m-%d')])
    date_end: datetime | None = Field(default=None,
                                      description='Дата окончания действия лицензии',
                                      examples=[None])

class licenses(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inn: str = Field(description='ИНН',
                     examples=['0123456789'])
    ogrn: str = Field(description='ОГРН',
                      examples=['0123456789012'])
    licenses_data: list[LICENSES_DATA]


class full_data(BaseModel):
    inn: str = Field(description='ИНН',
                     examples=['0123456789'])
    ogrn: str = Field(description='ОГРН',
                      examples=['0123456789012'])
    main_okved_name: str | None = Field(default=None,
                                        description='Наименование основново ОКВЭДа',
                                        examples=['Подача напитков'])
    main_okved_code: str | None = Field(default=None,
                                        description='Код основново ОКВЭДа',
                                        examples=['56.30'])
    full_name: str | None = Field(default=None,
                                  description='Полное наименование юридического лица',
                                  examples=['ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ "Ромашка"'])
    short_name: str | None = Field(default=None,
                                   description='Сокращенное наименование юридического лица',
                                   examples=['ООО "Ромашка"'])
    subject_type: str | None = Field(default=None,
                                     description='Вид субъекта МСП',
                                     examples=['юридическое лицо'])
    subject_category: str | None = Field(default=None,
                                         description='Категория субъекта МСП',
                                         examples=['микропредприятие'])
    inclusion_date: datetime | None = Field(default=None,
                                            description='Дата включения в реестр МСП',
                                            examples=[datetime.strptime('2025-12-10', '%Y-%m-%d')])
    is_social: bool | None = Field(default=None,
                                   description='Является ли социальным предприятием',
                                   examples=[True])
    region_code: str | None = Field(default=None,
                                    description='Код региона',
                                    examples=['42'])
    region: str | None = Field(default=None,
                               description='Субъект РФ',
                               examples=['обл. Кемеровская область - Кузбасс'])
    district: str | None = Field(default=None,
                                 description='Район',
                                 examples=['р-н Крапивинский'])
    area: str | None = Field(default=None,
                             description='Город',
                             examples=['пгт. Крапивинский'])

    additional_okveds_data: list[ADDITIONAL_OKVEDS_DATA] | None = list()

    licenses_data: list[LICENSES_DATA] | None = list()


__all__ = ['full_data', 'licenses', 'okveds', 'sno', 'fns_main_info']