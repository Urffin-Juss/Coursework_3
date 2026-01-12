import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class DBConfig:
    host: str
    port: str
    dbname: str
    user: str
    password: str



def get_db_config() -> DBConfig:
    return DBConfig(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME", "hh_project"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

