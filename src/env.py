from pathlib import Path

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(find_dotenv('.env'))

SRC_DIR = Path(__file__).parent

REPO_ROOT_DIR = SRC_DIR.parent


class Env(BaseSettings):
    # 3rd Party Services
    openai_api_key: str

    # Database Configuration
    mock_nosql_db_dir: Path = REPO_ROOT_DIR / 'database/mock_nosql_db'
    vector_db_dir: Path = REPO_ROOT_DIR / 'database/vector_db'

    model_config = SettingsConfigDict(
        env_file=find_dotenv('.env'),
        extra='ignore'
    )


env = Env()
