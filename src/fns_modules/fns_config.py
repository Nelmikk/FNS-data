from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic.fields import Field
from multiprocessing import cpu_count
import dotenv

dotenv.load_dotenv()

class Settings(BaseSettings):
    cpu_count: int = Field(default=1, gt=0, le=cpu_count())
    semaphore_count: int = Field(default=2, gt=1)
    model_config = SettingsConfigDict(env_file='.env', env_prefix='FNS_')

fns_settings = Settings()