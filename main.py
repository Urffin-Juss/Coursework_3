from config import get_db_config
from db_create import create_database_if_not_exists, create_tables
from db_fill import fill_db
from db_manager import DBManager



def format_salary(s_from, s_to, cur):
    if s_from is None and s_to is None:
        return "не указана"
    if s_from is not None and s_to is not None:
        return f"{s_from}–{s_to} {cur or ''}".strip()
    if s_from is not None:
        return f"от {s_from} {cur or ''}".strip()
    return f"до {s_to} {cur or ''}".strip()


def main():
    cfg = get_db_config()

    # ВАЖНО: вставь сюда минимум 10 employer_id
    employer_ids = [
        1740,   # Яндекс
        3529,   # Сбер
        78638,  # Тинькофф (может меняться)
        2180,   # Ozon (пример)
        87021,  # VK (пример)
        49357,  # Kaspersky (пример)
        3776,   # Альфа-Банк (пример)
        80,     # Ростелеком (пример)
        3127,   # Газпром нефть (пример)
        15478,  # МТС (пример)
    ]

    print("1) Создаю БД/таблицы...")
    cfg = get_db_config()

    print("host:", repr(cfg.host))
    print("port:", repr(cfg.port))
    print("dbname:", repr(cfg.dbname))
    print("user:", repr(cfg.user))
    print("password:", repr(cfg.password))

    create_database_if_not_exists(cfg)
    create_tables(cfg)

    print("2) Забираю данные с hh и заполняю таблицы...")
    fill_db(cfg, employer_ids)

    db = DBManager(cfg)

    while True:
        print("\nВыберите действие:")
        print("1 — Список компаний и количество вакансий")
        print("2 — Все вакансии (компания/вакансия/зп/ссылка)")
        print("3 — Средняя зарплата")
        print("4 — Вакансии с зарплатой выше средней")
        print("5 — Поиск вакансий по ключевому слову")
        print("0 — Выход")

        choice = input("Ваш выбор: ").strip()

        if choice == "0":
            break

        if choice == "1":
            rows = db.get_companies_and_vacancies_count()
            for name, cnt in rows:
                print(f"{name}: {cnt}")

        elif choice == "2":
            rows = db.get_all_vacancies()
            for company, vacancy, s_from, s_to, cur, url in rows:
                print(f"{company} | {vacancy} | {format_salary(s_from, s_to, cur)} | {url}")

        elif choice == "3":
            avg = db.get_avg_salary()
            print(f"Средняя зарплата: {avg:.2f}" if avg is not None else "Средняя зарплата: нет данных")

        elif choice == "4":
            rows = db.get_vacancies_with_higher_salary()
            for company, vacancy, s_from, s_to, cur, url in rows:
                print(f"{company} | {vacancy} | {format_salary(s_from, s_to, cur)} | {url}")

        elif choice == "5":
            kw = input("Введите слово (например python): ").strip()
            rows = db.get_vacancies_with_keyword(kw)
            for company, vacancy, s_from, s_to, cur, url in rows:
                print(f"{company} | {vacancy} | {format_salary(s_from, s_to, cur)} | {url}")

        else:
            print("Не понял выбор. Повторите.")


if __name__ == "__main__":
    main()
