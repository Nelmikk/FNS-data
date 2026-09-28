import uvicorn
from fastapi import FastAPI

from src.api_modules.api_endpoints import *


app = FastAPI()





@app.get('/v1/organisations/{value}')
async def get_organisation_info(value: str, ) -> list[api_models.fns_main_info] | str:
    return await get_organisation_info_endpoint(value=value)



@app.get('/v1/organisations/{value}/additional_okveds')
async def get_additional_okveds(value: str, ) -> list[api_models.okveds] | str:
    return await get_additional_okveds_endpoint(value=value)


@app.get('/v1/organisations/{value}/licenses')
async def get_licenses(value: str, ) -> list[api_models.licenses] | str:
    return await get_licenses_endpoint(value=value)


@app.get('/v1/organisations/{value}/sno')
async def get_sno(value: str, ) -> list[api_models.sno]:
    return await get_sno_endpoint(value=value)

@app.get('/v1/organisations/{value}/full_data')
async def get_full_organisation_data(value: str, ) -> list[api_models.full_data] | str:
    return await get_full_data(value=value)



if __name__ == '__main__':
    uvicorn.run('api:app', reload=True)
