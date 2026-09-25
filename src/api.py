import uvicorn
from fastapi import FastAPI

from src.models import api_models
from src.api_modules.api_endpoints import *


app = FastAPI()





@app.get('/v1/organisations/{value}')
async def get_organisation_info(value: int, ) -> list[api_models.fns_main_info] | str:
    return await get_organisation_info_endpoint(value=value)



@app.get('/v1/organisations/{value}/additional_okveds')
async def get_additional_okveds(value: int, ) -> list[api_models.okveds] | str:
    return await get_additional_okveds_endpoint(value=value)



@app.get('/v1/organisations/{value}/full_info')
async def get_full_organisation_data(value: int, ) -> list[api_models.full_info] | str:
    return await get_full_organisation_data_endpoint(value=value)



if __name__ == '__main__':
    uvicorn.run('api:app', reload=True)
