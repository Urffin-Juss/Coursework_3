import os
os.environ["PGCLIENTENCODING"] = "UTF8"
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
        host=os.getenv("DB_HOST").strip(),
        port=os.getenv("DB_PORT").strip(),
        dbname=os.getenv("DB_NAME").strip(),
        user=os.getenv("DB_USER").strip(),
        password=os.getenv("DB_PASSWORD").strip(),
    )

