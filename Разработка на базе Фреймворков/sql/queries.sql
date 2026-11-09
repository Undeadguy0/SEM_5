-- Список помещений
SELECT
    id,
    name,
    capacity,
    equipment
FROM rooms
ORDER BY name;

-- Список пользователей
SELECT
    id,
    name,
    email
FROM users
ORDER BY name;

-- Список бронирований
SELECT
    id,
    room_id,
    user_id,
    booking_date,
    start_time,
    end_time,
    topic,
    is_cancelled
FROM bookings
ORDER BY booking_date, start_time;

-- Поиск помещений по вместимости
SELECT
    id,
    name,
    capacity
FROM rooms
WHERE capacity >= 8
ORDER BY capacity;

-- Активные бронирования
SELECT
    id,
    room_id,
    user_id,
    booking_date,
    topic
FROM bookings
WHERE is_cancelled = 0
ORDER BY booking_date;

-- Помещения с проектором
SELECT
    id,
    name,
    equipment
FROM rooms
WHERE equipment LIKE '%проектор%'
ORDER BY name;

-- Полная информация об активном бронировании
SELECT
    bookings.id,
    bookings.booking_date,
    bookings.start_time,
    bookings.end_time,
    bookings.topic,
    rooms.name AS room_name,
    rooms.capacity,
    users.name AS user_name,
    users.email AS user_email
FROM bookings
JOIN rooms
    ON bookings.room_id = rooms.id
JOIN users
    ON bookings.user_id = users.id
WHERE bookings.is_cancelled = 0
ORDER BY bookings.booking_date, bookings.start_time;

-- Все бронирования с названием помещения и именем организатора
SELECT
    bookings.id,
    bookings.booking_date,
    bookings.is_cancelled,
    rooms.name AS room_name,
    users.name AS user_name
FROM bookings
JOIN rooms
    ON bookings.room_id = rooms.id
JOIN users
    ON bookings.user_id = users.id
ORDER BY bookings.id;

-- Свободные помещения на выбранную дату
-- В приложении дата передаётся параметром ?, здесь пример для проверки.
SELECT
    rooms.id,
    rooms.name,
    rooms.capacity,
    rooms.equipment
FROM rooms
WHERE rooms.id NOT IN (
    SELECT bookings.room_id
    FROM bookings
    WHERE bookings.booking_date = '2026-09-29'
        AND bookings.is_cancelled = 0
)
ORDER BY rooms.name;

-- Количество активных бронирований
SELECT
    COUNT(*) AS bookings_count
FROM bookings
WHERE is_cancelled = 0;

-- Сводка по помещениям
SELECT
    COUNT(*) AS rooms_count,
    AVG(capacity) AS average_capacity,
    MAX(capacity) AS max_capacity
FROM rooms;

-- Количество активных бронирований по помещениям
SELECT
    rooms.name AS room_name,
    COUNT(bookings.id) AS bookings_count
FROM rooms
LEFT JOIN bookings
    ON rooms.id = bookings.room_id
    AND bookings.is_cancelled = 0
GROUP BY rooms.id, rooms.name
ORDER BY bookings_count DESC;

-- Количество активных бронирований по организаторам
SELECT
    users.name AS user_name,
    COUNT(bookings.id) AS bookings_count
FROM users
LEFT JOIN bookings
    ON users.id = bookings.user_id
    AND bookings.is_cancelled = 0
GROUP BY users.id, users.name
ORDER BY bookings_count DESC;

-- Помещения, забронированные больше одного раза
SELECT
    rooms.name AS room_name,
    COUNT(bookings.id) AS bookings_count
FROM rooms
JOIN bookings
    ON rooms.id = bookings.room_id
WHERE bookings.is_cancelled = 0
GROUP BY rooms.id, rooms.name
HAVING COUNT(bookings.id) > 1
ORDER BY bookings_count DESC;

-- Две самые вместительные переговорные
SELECT
    id,
    name,
    capacity
FROM rooms
ORDER BY capacity DESC
LIMIT 2;
