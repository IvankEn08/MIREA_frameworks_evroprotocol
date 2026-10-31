import json

from db.database import BASE_DIR, get_connection
from db.init_db import initialize_database


def load_json(filename: str) -> list[dict]:
    path = BASE_DIR / "data" / filename
    return json.loads(path.read_text(encoding="utf-8"))


def import_data() -> None:
    initialize_database()
    accidents = load_json("accidents.json")
    participants = load_json("participants.json")
    vehicles = load_json("vehicles.json")
    messages = load_json("emergency_messages.json")

    with get_connection() as connection:
        connection.execute("DELETE FROM emergency_messages")
        connection.execute("DELETE FROM participants")
        connection.execute("DELETE FROM vehicles")
        connection.execute("DELETE FROM accidents")
        connection.executemany(
            """
            INSERT INTO accidents (
                id, location, occurred_at, has_injured, has_fire, status
            ) VALUES (
                :id, :location, :occurred_at, :has_injured, :has_fire, :status
            )
            """,
            accidents,
        )
        connection.executemany(
            """
            INSERT INTO vehicles (id, plate_number, brand, model)
            VALUES (:id, :plate_number, :brand, :model)
            """,
            vehicles,
        )
        connection.executemany(
            """
            INSERT INTO participants (
                id, accident_id, vehicle_id, full_name, phone
            ) VALUES (
                :id, :accident_id, :vehicle_id, :full_name, :phone
            )
            """,
            participants,
        )
        connection.executemany(
            """
            INSERT INTO emergency_messages (
                id, accident_id, service_name, sent_at, status
            ) VALUES (
                :id, :accident_id, :service_name, :sent_at, :status
            )
            """,
            messages,
        )


if __name__ == "__main__":
    import_data()
    print("Данные из JSON импортированы в SQLite.")
