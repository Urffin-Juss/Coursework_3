import psycopg2
from config import DBConfig


class DBManager:
    def __init__(self, cfg: DBConfig):
        self.cfg = cfg

    def _connect(self):
        return psycopg2.connect(
            host=self.cfg.host,
            port=self.cfg.port,
            dbname=self.cfg.dbname,
            user=self.cfg.user,
            password=self.cfg.password,
        )

    def get_companies_and_vacancies_count(self):
        """
        список всех компаний и количество вакансий у каждой компании
        """
        q = """
        SELECT e.name, COUNT(v.vacancy_id) AS вакансий
        FROM employers e
        LEFT JOIN vacancies v ON v.employer_id = e.employer_id
        GROUP BY e.name
        ORDER BY вакансий DESC, e.name;
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(q)
                return cur.fetchall()

    def get_all_vacancies(self):
        """
        список всех вакансий: компания, вакансия, зарплата (from/to/currency), ссылка
        """
        q = """
        SELECT e.name AS company,
               v.name AS vacancy,
               v.salary_from,
               v.salary_to,
               v.salary_currency,
               v.alternate_url
        FROM vacancies v
        JOIN employers e ON e.employer_id = v.employer_id
        ORDER BY company, vacancy;
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(q)
                return cur.fetchall()

    def get_avg_salary(self):
        """
        средняя зарплата по вакансиям
        Берём "среднее из середины вилки" (salary_from+salary_to)/2,
        если одно из значений NULL — берём второе.
        """
        q = """
        SELECT AVG(
            CASE
                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN (salary_from + salary_to) / 2.0
                WHEN salary_from IS NOT NULL THEN salary_from
                WHEN salary_to IS NOT NULL THEN salary_to
                ELSE NULL
            END
        ) AS avg_salary
        FROM vacancies;
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(q)
                row = cur.fetchone()
                return row[0]

    def get_vacancies_with_higher_salary(self):
        """
        вакансии, у которых зарплата выше средней (по логике выше)
        """
        q = """
        WITH avg_sal AS (
            SELECT AVG(
                CASE
                    WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN (salary_from + salary_to) / 2.0
                    WHEN salary_from IS NOT NULL THEN salary_from
                    WHEN salary_to IS NOT NULL THEN salary_to
                    ELSE NULL
                END
            ) AS a
            FROM vacancies
        )
        SELECT e.name AS company,
               v.name AS vacancy,
               v.salary_from, v.salary_to, v.salary_currency,
               v.alternate_url
        FROM vacancies v
        JOIN employers e ON e.employer_id = v.employer_id
        CROSS JOIN avg_sal
        WHERE
            CASE
                WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL THEN (v.salary_from + v.salary_to) / 2.0
                WHEN v.salary_from IS NOT NULL THEN v.salary_from
                WHEN v.salary_to IS NOT NULL THEN v.salary_to
                ELSE NULL
            END > avg_sal.a
        ORDER BY company, vacancy;
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(q)
                return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str):
        """
        вакансии, в названии которых содержится keyword (LIKE)
        """
        q = """
        SELECT e.name AS company,
               v.name AS vacancy,
               v.salary_from, v.salary_to, v.salary_currency,
               v.alternate_url
        FROM vacancies v
        JOIN employers e ON e.employer_id = v.employer_id
        WHERE v.name ILIKE %s
        ORDER BY company, vacancy;
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(q, (f"%{keyword}%",))
                return cur.fetchall()
