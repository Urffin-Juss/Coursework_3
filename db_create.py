import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import DBConfig


def create_database_if_not_exists(cfg: DBConfig) -> None:
    """
    Подключаемся к postgres (системной БД) и создаём целевую, если нет.
    """
    conn = psycopg2.connect(
        host=cfg.host, port=cfg.port, dbname="postgres", user=cfg.user, password=cfg.password
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname=%s;", (cfg.dbname,))
        exists = cur.fetchone() is not None
        if not exists:
            cur.execute(f'CREATE DATABASE "{cfg.dbname}";')
    conn.close()


def create_tables(cfg: DBConfig) -> None:
    conn = psycopg2.connect(
        host=cfg.host, port=cfg.port, dbname=cfg.dbname, user=cfg.user, password=cfg.password
    )
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS employers (
                    employer_id BIGINT PRIMARY KEY,
                    name TEXT NOT NULL,
                    url TEXT
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS vacancies (
                    vacancy_id BIGINT PRIMARY KEY,
                    employer_id BIGINT NOT NULL REFERENCES employers(employer_id) ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    salary_from INTEGER,
                    salary_to INTEGER,
                    salary_currency TEXT,
                    alternate_url TEXT
                );
            """)
    conn.close()
