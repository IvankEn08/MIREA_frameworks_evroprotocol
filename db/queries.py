from db.database import get_connection


def fetch_all(sql: str, parameters: tuple = ()) -> list[dict]:
    with get_connection() as connection:
        rows = connection.execute(sql, parameters).fetchall()
    return [dict(row) for row in rows]


def fetch_one(sql: str, parameters: tuple = ()) -> dict | None:
    with get_connection() as connection:
        row = connection.execute(sql, parameters).fetchone()
    return dict(row) if row else None


def get_accidents() -> list[dict]:
    return fetch_all(
        """
        SELECT id, location, occurred_at, has_injured, has_fire, status,
               CASE
                 WHEN has_injured = 1 OR has_fire = 1
                 THEN 'Повышенная опасность'
                 ELSE 'Без пострадавших'
               END AS category
        FROM accidents
        ORDER BY occurred_at DESC
        """
    )


def get_recent_accidents(limit: int = 3) -> list[dict]:
    return fetch_all(
        """
        SELECT id, location, occurred_at, status
        FROM accidents
        ORDER BY occurred_at DESC
        LIMIT ?
        """,
        (limit,),
    )


def get_accident(accident_id: int) -> dict | None:
    accident = fetch_one(
        """
        SELECT a.id, a.location, a.occurred_at, a.has_injured,
               a.has_fire, a.status, COUNT(p.id) AS participant_count
        FROM accidents AS a
        LEFT JOIN participants AS p ON p.accident_id = a.id
        WHERE a.id = ?
        GROUP BY a.id
        """,
        (accident_id,),
    )
    if accident:
        accident["participants"] = fetch_all(
            """
            SELECT p.full_name, p.phone, v.brand, v.model, v.plate_number
            FROM participants AS p
            JOIN vehicles AS v ON v.id = p.vehicle_id
            WHERE p.accident_id = ?
            ORDER BY p.full_name
            """,
            (accident_id,),
        )
        accident["messages"] = fetch_all(
            """
            SELECT service_name, sent_at, status
            FROM emergency_messages
            WHERE accident_id = ?
            ORDER BY sent_at
            """,
            (accident_id,),
        )
    return accident


def get_accidents_by_severity(severity: str) -> list[dict]:
    conditions = {
        "emergency": "has_injured = 1 OR has_fire = 1",
        "regular": "has_injured = 0 AND has_fire = 0",
        "injured": "has_injured = 1",
        "fire": "has_fire = 1",
    }
    condition = conditions.get(severity)
    if condition is None:
        return []
    return fetch_all(
        f"""
        SELECT id, location, occurred_at, status
        FROM accidents
        WHERE {condition}
        ORDER BY occurred_at DESC
        """
    )


def get_participants_with_accidents() -> list[dict]:
    return fetch_all(
        """
        SELECT p.full_name, p.phone, a.id AS accident_id, a.location,
               v.brand, v.model, v.plate_number
        FROM participants AS p
        JOIN accidents AS a ON a.id = p.accident_id
        JOIN vehicles AS v ON v.id = p.vehicle_id
        ORDER BY a.occurred_at DESC, p.full_name
        """
    )


def get_statistics_by_category() -> list[dict]:
    return fetch_all(
        """
        SELECT CASE
                 WHEN has_injured = 1 OR has_fire = 1
                 THEN 'Повышенная опасность'
                 ELSE 'Без пострадавших'
               END AS category,
               COUNT(*) AS accident_count
        FROM accidents
        GROUP BY category
        ORDER BY accident_count DESC
        """
    )


def get_statistics_by_location() -> list[dict]:
    return fetch_all(
        """
        SELECT location, COUNT(*) AS accident_count
        FROM accidents
        GROUP BY location
        HAVING COUNT(*) >= 1
        ORDER BY accident_count DESC, location
        """
    )


def get_dashboard_statistics() -> dict:
    return fetch_one(
        """
        SELECT COUNT(*) AS total,
               SUM(CASE WHEN has_injured = 1 OR has_fire = 1
                        THEN 1 ELSE 0 END) AS emergencies,
               SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) AS closed
        FROM accidents
        """
    ) or {"total": 0, "emergencies": 0, "closed": 0}
