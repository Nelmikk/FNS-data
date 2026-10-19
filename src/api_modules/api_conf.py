import dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.fields import Field

dotenv.load_dotenv()


class ApiSettings(BaseSettings):
    app: str = 'app:api'
    host: str = '0.0.0.0'
    port: int = 8000
    reload: bool = True
    workers: int = Field(default=6, gt=0)

    model_config = SettingsConfigDict(env_file='.env', env_prefix='API_')


class ApiEngineSettings(BaseSettings):
    pool_size: int = Field(default=6, gt=0)
    max_overflow: int = Field(default=4, gt=0)

    model_config = SettingsConfigDict(env_file='.env', env_prefix='API_Engine_')

