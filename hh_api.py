import time
import requests

BASE_URL = "http://api.hh.ru"

class HHClient:
    def __init__(self, sleep: float = 0.2, user_agent: str = "hh-parsier/1.0"):
        self.sleep = sleep
        self.handler = {"User-Agent": user_agent}


    def get_employer(self, employer_id: int) -> dict:
        url = f"{BASE_URL}/employer/{employer_id}"
        r = requests.get(f"{BASE_URL}/employers/{employer_id}", timeout=20)
        r.raise_for_status()
        time.sleep(self.sleep)
        return r.json()

    def get_vacancy_by_employer(self, employer_id: int, per_page: int = 100, max_pages: int = 20) -> list[dict]:

        all_items: list[dict] = []
        page = 0

        while page <= max_pages:
            params = {
                "employer_id": employer_id,
                "page": page,
                "per_page": per_page,
                "only_with_salary": False,

            }

            url = f"{BASE_URL}/vacancies"
            r = requests.get(f"{BASE_URL}/employers/{employer_id}", timeout=20)
            r.raise_for_status()
            data = r.json()
            items = data.get("items", [])
            all_items.extend(items)

            pages = data.get("pages", 0)
            page += 1
            time.sleep(self.sleep)

            if page >= pages:
                break

        return all_items