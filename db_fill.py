import psycopg2
from config import DBConfig
from hh_api import HHClient


def upsert_employer(cur, employer: dict) -> None:
    cur.execute(
        """
        INSERT INTO employers (employer_id, name, url)
        VALUES (%s, %s, %s)
        ON CONFLICT (employer_id) DO UPDATE
        SET name = EXCLUDED.name,
            url = EXCLUDED.url;
        """,
        (
            int(employer["id"]),
            employer.get("name"),
            employer.get("alternate_url") or employer.get("url"),
        ),
    )


def upsert_vacancy(cur, employer_id: int, vacancy_item: dict) -> None:
    salary = vacancy_item.get("salary") or {}
    cur.execute(
        """
        INSERT INTO vacancies (vacancy_id, employer_id, name, salary_from, salary_to, salary_currency, alternate_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (vacancy_id) DO UPDATE
        SET employer_id = EXCLUDED.employer_id,
            name = EXCLUDED.name,
            salary_from = EXCLUDED.salary_from,
            salary_to = EXCLUDED.salary_to,
            salary_currency = EXCLUDED.salary_currency,
            alternate_url = EXCLUDED.alternate_url;
        """,
        (
            int(vacancy_item["id"]),
            employer_id,
            vacancy_item.get("name"),
            salary.get("from"),
            salary.get("to"),
            salary.get("currency"),
            vacancy_item.get("alternate_url"),
        ),
    )


def fill_db(cfg: DBConfig, employer_ids: list[int]) -> None:
    hh = HHClient(sleep=0.2)

    conn = psycopg2.connect(
        host=cfg.host, port=cfg.port, dbname=cfg.dbname, user=cfg.user, password=cfg.password
    )
    with conn:
        with conn.cursor() as cur:
            for emp_id in employer_ids:
                employer = hh.get_employer(emp_id)
                upsert_employer(cur, employer)

                vacancies = hh.get_vacancies_by_employer(emp_id)
                for v in vacancies:
                    upsert_vacancy(cur, emp_id, v)

    conn.close()
