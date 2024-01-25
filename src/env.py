from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(find_dotenv('.env'))


class Env(BaseSettings):
    openai_api_key: str

    model_config = SettingsConfigDict(
        env_file=find_dotenv('.env'),
        extra='ignore'
    )


env = Env()
