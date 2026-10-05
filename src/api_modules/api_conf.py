import dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.fields import Field

dotenv.load_dotenv()


class ApiSettings(BaseSettings):
    app: str = 'app:api'
    host: str = 'localhost'
    port: int = 8000
    reload: bool = True
    workers: int = Field(default=8, gt=0)

    model_config = SettingsConfigDict(env_file='.env', env_prefix='API_')


class ApiEngineSettings(BaseSettings):
    pool_size: int = Field(default=5, gt=0)
    max_overflow: int = Field(default=10, gt=0)

    model_config = SettingsConfigDict(env_file='.env', env_prefix='API_Engine_')

