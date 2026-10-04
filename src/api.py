import uvicorn
from fastapi import FastAPI
from src.models.api_models import *
from src.api_modules.api_conf import app_settings

from src.api_modules.api_endpoints import *


app = FastAPI()





@app.get('/v1/organisations/{value}')
async def get_organisation_info(value: str, ) -> list[fns_main_info | None]:
    """
    Получение основной инфы по организации.
        Если организация не найдена, то вернется пустой список
    :param value:
    :return:
    """
    return await get_organisation_info_endpoint(value=value)


@app.get('/v1/organisations/{value}/additional_okveds')
async def get_additional_okveds(value: str, ) -> list[okveds | None]:
    """
    Получение дополнительных ОКВЭДов по ИНН/ОГРН организации.
        Если организация не найдена, то вернется пустой список.
    :param value:
    :return:
    """
    return await get_additional_okveds_endpoint(value=value)


@app.get('/v1/organisations/{value}/licenses')
async def get_licenses(value: str, ) -> list[licenses | None]:
    """
    Получение сведений о лицензиях по ИНН/ОГРН организации.
        Если организация не найдена, то вернется пустой список
    :param value:
    :return:
    """
    return await get_licenses_endpoint(value=value)


@app.get('/v1/organisations/{value}/sno')
async def get_sno(value: str, ) -> list[sno | None]:
    """
    Получение сведений об СНО по ИНН/ОГРН организации.
        Если организация не найдена, то вернется пустой список.
    :param value:
    :return:
    """
    return await get_sno_endpoint(value=value)


@app.get('/v1/organisations/{value}/full_data')
async def get_full_organisation_data(value: str, ) -> list[full_data | None] | str:
    """
    Получение всей доступной инфы по ИНН/ОГРН организации.
        Если организация не найдена, то вернется пустой список
    :param value:
    :return:
    """
    return await get_full_data(value=value)



if __name__ == '__main__':
    uvicorn.run(**app_settings.model_dump())
