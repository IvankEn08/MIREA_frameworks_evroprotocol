-- 1-2. Выборка списков
SELECT id, location, occurred_at, status
FROM accidents ORDER BY occurred_at DESC;

SELECT id, plate_number, brand, model
FROM vehicles ORDER BY brand, model;

-- 3-4. Фильтрация WHERE
SELECT id, location, occurred_at
FROM accidents WHERE has_injured = 1 OR has_fire = 1;

SELECT id, location, occurred_at
FROM accidents WHERE status = 'closed';

-- 5-6. JOIN
SELECT p.full_name, a.location, v.brand, v.model, v.plate_number
FROM participants AS p
JOIN accidents AS a ON a.id = p.accident_id
JOIN vehicles AS v ON v.id = p.vehicle_id;

SELECT a.id, a.location, m.service_name, m.sent_at, m.status
FROM accidents AS a
JOIN emergency_messages AS m ON m.accident_id = a.id;

-- 7-8. Агрегатные функции
SELECT COUNT(*) AS accident_count FROM accidents;

SELECT COUNT(*) AS emergency_count
FROM accidents WHERE has_injured = 1 OR has_fire = 1;

-- 9-10. GROUP BY
SELECT status, COUNT(*) AS accident_count
FROM accidents GROUP BY status;

SELECT a.location, COUNT(p.id) AS participant_count
FROM accidents AS a
LEFT JOIN participants AS p ON p.accident_id = a.id
GROUP BY a.id, a.location ORDER BY participant_count DESC;

