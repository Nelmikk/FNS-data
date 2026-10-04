from pydantic_settings import SettingsConfigDict, BaseSettings
import dotenv

dotenv.load_dotenv()

class Settings(BaseSettings):
    cpu_count: int = 1
    semaphore_count: int = 2
    model_config = SettingsConfigDict(env_file='.env', env_prefix='FNS_')

fns_settings = Settings()