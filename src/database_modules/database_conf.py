from sqlalchemy.engine import create_engine
from sqlalchemy import text
from dotenv import load_dotenv

from pydantic_settings import SettingsConfigDict, BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """
    Класс для хранения данных для создания Engine-объектов.
    """
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    @property
    def DATABASE_URL_ASYNC(self, ) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    @property
    def DATABASE_URL(self, ) -> str:
        return f'postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

class SettingsSuperUser(Settings):
    model_config = SettingsConfigDict(env_file='.env',  env_prefix='SUPER_USER_')


class SettingsSelectUser(Settings):
    model_config = SettingsConfigDict(env_file='.env', env_prefix='SELECT_USER_')


settings_super_user = SettingsSuperUser()
settings_select_user = SettingsSelectUser()



def create_readonly_user():
    """
    Создание read-only юзера и выдача ему прав на чтение существующих таблиц и созданных поздее таблиц пользователем,
        который эти права дает.
    :return:
    """
    engine = create_engine(settings_super_user.DATABASE_URL)

    create_user_query = text(f"CREATE ROLE {settings_select_user.DB_USER} LOGIN PASSWORD '{settings_select_user.DB_PASSWORD}';")

    # Позволяет коннектиться
    grant_connect_query = text(f'GRANT CONNECT ON DATABASE {settings_select_user.DB_NAME} to {settings_select_user.DB_USER};')
    # Позволяет читать существующие таблицы
    grant_select_query = text(f'GRANT SELECT ON ALL TABLES IN SCHEMA public TO {settings_select_user.DB_USER};')
    # Позволяет читать будущие таблицы
    set_default_privileges_query = text(f'ALTER DEFAULT PRIVILEGES FOR ROLE {settings_super_user.DB_USER} IN SCHEMA public GRANT SELECT ON TABLES TO {settings_select_user.DB_USER};')

    with engine.connect() as connection:
        connection.execute(create_user_query)
        connection.execute(grant_connect_query)
        connection.execute(grant_select_query)
        connection.execute(set_default_privileges_query)
        connection.commit()
