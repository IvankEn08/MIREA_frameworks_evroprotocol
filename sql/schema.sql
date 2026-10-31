PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS accidents (
    id INTEGER PRIMARY KEY,
    location TEXT NOT NULL,
    occurred_at TEXT NOT NULL,
    has_injured INTEGER NOT NULL DEFAULT 0,
    has_fire INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'new'
);

CREATE TABLE IF NOT EXISTS vehicles (
    id INTEGER PRIMARY KEY,
    plate_number TEXT NOT NULL UNIQUE,
    brand TEXT NOT NULL,
    model TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS participants (
    id INTEGER PRIMARY KEY,
    accident_id INTEGER NOT NULL,
    vehicle_id INTEGER NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    FOREIGN KEY (accident_id) REFERENCES accidents(id),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
);

CREATE TABLE IF NOT EXISTS emergency_messages (
    id INTEGER PRIMARY KEY,
    accident_id INTEGER NOT NULL,
    service_name TEXT NOT NULL,
    sent_at TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (accident_id) REFERENCES accidents(id)
);

