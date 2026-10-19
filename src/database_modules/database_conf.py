from dotenv import load_dotenv

from pydantic_settings import SettingsConfigDict, BaseSettings

load_dotenv()



class SettingsSuperUser(BaseSettings):
    """
    Класс для хранения данных супер юзера при создании пулов соединений.
    """
    host: str
    port: int
    name: str
    super_user_name: str
    super_user_password: str

    model_config = SettingsConfigDict(env_file='.env', env_prefix='DB_')

    @property
    def DATABASE_URL_ASYNC(self, ) -> str:
        return f'postgresql+asyncpg://{self.super_user_name}:{self.super_user_password}@{self.host}:{self.port}/{self.name}'

    @property
    def DATABASE_URL(self, ) -> str:
        return f'postgresql+psycopg://{self.super_user_name}:{self.super_user_password}@{self.host}:{self.port}/{self.name}'


class SettingsSelectUser(BaseSettings):
    """
    Класс для хранения данных селект юзера при создании пулов соединений.
    """
    host: str
    port: int
    name: str
    select_user_name: str
    select_user_password: str

    model_config = SettingsConfigDict(env_file='.env', env_prefix='DB_')

    @property
    def DATABASE_URL_ASYNC(self, ) -> str:
        return f'postgresql+asyncpg://{self.select_user_name}:{self.select_user_password}@{self.host}:{self.port}/{self.name}'

    @property
    def DATABASE_URL(self, ) -> str:
        return f'postgresql+psycopg://{self.select_user_name}:{self.select_user_password}@{self.host}:{self.port}/{self.name}'


settings_super_user = SettingsSuperUser()
settings_select_user = SettingsSelectUser()



# def create_readonly_user():
#     """
#     Создание read-only юзера и выдача ему прав на чтение существующих таблиц и созданных поздее таблиц пользователем,
#         который эти права дает.
#     :return:
#     """
#     engine = create_engine(settings_super_user.DATABASE_URL)
#
#     create_user_query = text(f"CREATE ROLE {settings_select_user.DB_USER} LOGIN PASSWORD '{settings_select_user.DB_PASSWORD}';")
#
#     # Позволяет коннектиться
#     grant_connect_query = text(f'GRANT CONNECT ON DATABASE {settings_select_user.DB_NAME} to {settings_select_user.DB_USER};')
#     # Позволяет читать существующие таблицы
#     grant_select_query = text(f'GRANT SELECT ON ALL TABLES IN SCHEMA public TO {settings_select_user.DB_USER};')
#     # Позволяет читать будущие таблицы
#     set_default_privileges_query = text(f'ALTER DEFAULT PRIVILEGES FOR ROLE {settings_super_user.DB_USER} IN SCHEMA public GRANT SELECT ON TABLES TO {settings_select_user.DB_USER};')
#
#     with engine.connect() as connection:
#         connection.execute(create_user_query)
#         connection.execute(grant_connect_query)
#         connection.execute(grant_select_query)
#         connection.execute(set_default_privileges_query)
#         connection.commit()
