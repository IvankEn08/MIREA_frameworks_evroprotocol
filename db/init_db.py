from db.database import BASE_DIR, get_connection


def initialize_database() -> None:
    schema = (BASE_DIR / "sql" / "schema.sql").read_text(encoding="utf-8")
    with get_connection() as connection:
        connection.executescript(schema)


if __name__ == "__main__":
    initialize_database()
    print("Структура базы данных создана.")
