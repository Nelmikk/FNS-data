import dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import fields

dotenv.load_dotenv()


class Settings(BaseSettings):
    app: str = 'app:api'
    host: str = 'localhost'
    port: int = 8000
    reload: bool = True
    workers: int = fields.Field(default=8, gt=0)

    model_config = SettingsConfigDict(env_file='.env', env_prefix='API_')



app_settings = Settings()


