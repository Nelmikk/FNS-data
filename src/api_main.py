import uvicorn

from src.models import api_models, database_models
from fastapi import FastAPI, HTTPException
from database_modules import orm
import asyncio

app = FastAPI()


search_type_organisation_info = {
    12: orm.select_fns_main_info_by_inn_async,       # Поиск по ИНН физ лиц
    10: orm.select_fns_main_info_by_inn_async,       # Поиск по ИНН юр лиц
    13: orm.select_fns_main_info_by_ogrn_async,      # Поиск по ОГРН
    15: orm.select_fns_main_info_by_ogrn_async,      # Поиск по ОГРН
}
search_type_additional_okveds = {
    12: orm.select_additional_okveds_by_inn_async,   # Поиск по ИНН физ лиц
    10: orm.select_additional_okveds_by_inn_async,   # Поиск по ИНН юр лиц
    13: orm.select_additional_okveds_by_ogrn_async,  # Поиск по ОГРН
    15: orm.select_additional_okveds_by_ogrn_async,  # Поиск по ОГРН
}


@app.get('/v1/organisations/{value}')
async def get_organisation_info(value: int, ) -> list[api_models.fns_main_info] | str:
    val_len = len(str(value))
    if not val_len in search_type_organisation_info.keys():
        raise HTTPException(status_code=400, detail='ValueError')

    results = await asyncio.create_task(search_type_organisation_info[val_len](value))

    if not results:
        raise HTTPException(404, detail='Not found')
    return [api_models.fns_main_info.model_validate(result) for result in results.all()]
    ...



@app.get('/v1/organisations/{value}/additional_okveds')
async def get_additional_okveds(value: int, ) -> list[api_models.okveds] | str:
    val_len = len(str(value))
    if not val_len in search_type_additional_okveds.keys():
        raise HTTPException(status_code=400, detail='ValueError')

    results = await asyncio.create_task(search_type_additional_okveds[val_len](value))

    if not results:
        raise HTTPException(404, detail='Not found')
    return [api_models.okveds.model_validate(result) for result in results.all()]
    ...



@app.get('/v1/organisations/{value}/full_info')
async def get_full_organisation_data(value: int, ) -> list[api_models.full_info] | str:
    val_len = len(str(value))
    if not val_len in search_type_organisation_info.keys():
        raise HTTPException(status_code=400, detail='ValueError')

    results = await asyncio.create_task(search_type_organisation_info[val_len](value))

    if not results:
        raise HTTPException(status_code=404, detail='Not found')
    results = [api_models.full_info.model_validate(result) for result in results.all()]
    response = []
    for result in results:
        results_okveds = await asyncio.create_task(
            orm.select_additional_okveds_by_ogrn_async(
                result.ogrn, *(database_models.okveds.name, database_models.okveds.code) ) )
        result.additional_okveds = [api_models.full_info_ovkeds.model_validate(i) for i in results_okveds.all()]
        response.append(result)
    return response
    ...


# import time
# ts = time.time()
# print(asyncio.run(get_organisation_info(384905790288)))
# print(time.time()-ts)


if __name__ == '__main__':
    uvicorn.run('api_main:app', reload=True)
