from fastapi import HTTPException

from src.models import api_models
from src.database_modules.select_queries.queries import *


# Словари для быстрого доступа к функциям, возвращающим запрошенную инфу.
# Возвращаемая функция зависит от кол-ва символов:
#   10 - ИНН юр лица
#   12 - ИНН физ лица
#   13 - ОГРН юр лица
#   15 - ОГРН физ лица

search_type_organisation_info = {
    12: select_fns_main_info_by_inn_async,              # Поиск по ИНН физ лиц
    10: select_fns_main_info_by_inn_async,              # Поиск по ИНН юр лиц
    13: select_fns_main_info_by_ogrn_async,             # Поиск по ОГРН
    15: select_fns_main_info_by_ogrn_async,             # Поиск по ОГРН
}

search_type_additional_okveds = {
    12: select_additional_okveds_by_inn_async,          # Поиск по ИНН физ лиц
    10: select_additional_okveds_by_inn_async,          # Поиск по ИНН юр лиц
    13: select_additional_okveds_by_ogrn_async,         # Поиск по ОГРН
    15: select_additional_okveds_by_ogrn_async,         # Поиск по ОГРН
}

search_type_licenses = {
    12: select_licenses_by_inn_async,                   # Поиск по ИНН физ лиц
    10: select_licenses_by_inn_async,                   # Поиск по ИНН юр лиц
    13: select_licenses_by_ogrn_async,                  # Поиск по ОГРН
    15: select_licenses_by_ogrn_async,                  # Поиск по ОГРН
}

search_type_sno = {
    12: select_sno_ip_by_inn_async,                     # Поиск по ИНН физ лиц
    10: select_sno_ul_by_inn_async,                     # Поиск по ИНН юр лиц
    13: select_sno_ul_by_ogrn_async,                    # Поиск по ОГРН юр лиц
    15: select_sno_ip_by_ogrn_async,                    # Поиск по ОГРН физ лиц
}

search_type_full_data = {
    12: select_full_data_ip_by_inn_async,               # Поиск по ИНН физ лиц
    10: select_full_data_ul_by_inn_async,               # Поиск по ИНН юр лиц
    13: select_full_data_ul_by_ogrn_async,              # Поиск по ОГРН юр лиц
    15: select_full_data_ip_by_ogrn_async,              # Поиск по ОГРН физ лиц
}


async def get_organisation_info_endpoint(value: str, ) -> list[api_models.fns_main_info]:
    val_len = len(value)
    if not val_len in search_type_organisation_info.keys():
        raise HTTPException(status_code=400, detail='ValueError')

    results = await search_type_organisation_info[val_len](value)

    return [api_models.fns_main_info.model_validate(result) async for result in results if result is not None]



async def get_additional_okveds_endpoint(value: str, ) -> list[api_models.okveds]:
    val_len = len(value)
    if not val_len in search_type_additional_okveds.keys():
        raise HTTPException(status_code=400, detail='ValueError')

    results = await search_type_additional_okveds[val_len](value)

    return [api_models.okveds.model_validate(result) async for result in results if result is not None]


async def get_licenses_endpoint(value: str, ) -> list[api_models.licenses]:
    val_len = len(value)
    if val_len not in search_type_licenses.keys():
        raise HTTPException(status_code=400, detail='ValueError')

    results = await search_type_licenses[val_len](value)

    return [api_models.licenses.model_validate(result) async for result in results if result is not None]


async def get_sno_endpoint(value: str, ) -> list[api_models.sno]:
    val_len = len(value)
    if val_len not in search_type_sno.keys():
        raise HTTPException(status_code=400, detail='ValueError')

    results = await search_type_sno[val_len](value)

    return [api_models.sno.model_validate(result) async for result in results if result is not None]


async def get_full_data(value: str, ) -> list[api_models.full_data]:
    val_len = len(value)
    if val_len not in search_type_full_data.keys():
        raise HTTPException(status_code=400, detail='ValueError')

    results = await search_type_full_data[val_len](value)

    return [api_models.full_data.model_validate(result) async for result in results if result is not None]


__all__ = ['get_full_data', 'get_licenses_endpoint', 'get_sno_endpoint',
           'get_organisation_info_endpoint', 'get_additional_okveds_endpoint']