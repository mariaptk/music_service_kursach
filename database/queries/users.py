# database/queries/users.py
# Аутентификация
AUTHENTICATE_USER = """
SELECT user_id, username, password_hash, role_id 
FROM users 
WHERE (username = %s OR email = %s) AND is_active = true
"""

# Регистрация
CREATE_USER = """
INSERT INTO users (username, email, password_hash, first_name, last_name, role_id) 
VALUES (%s, %s, %s, %s, %s, 1)
"""

# Получение пользователя
GET_USER_BY_ID = """
SELECT user_id, username, email, first_name, last_name, role_id, 
       avatar_url, date_registered, last_login 
FROM users 
WHERE user_id = %s
"""

# Статистика пользователя
USER_LISTENING_STATS = """
SELECT 
    COUNT(DISTINCT track_id) as unique_tracks_listened,
    COUNT(*) as total_listens,
    COALESCE(SUM(listen_duration_seconds), 0) as total_listen_seconds,
    AVG(listen_duration_seconds) as avg_listen_duration
FROM listen_history 
WHERE user_id = %s
"""

# Системная статистика
SYSTEM_STATS = """
SELECT 
    (SELECT COUNT(*) FROM users) as total_users,
    (SELECT COUNT(*) FROM tracks) as total_tracks,
    (SELECT COUNT(*) FROM artists) as total_artists,
    (SELECT COUNT(*) FROM listen_history) as total_listens
"""

# Все пользователи
GET_ALL_USERS = """
SELECT user_id, username, email, first_name, last_name, role_id, 
       date_registered, last_login, is_active 
FROM users 
ORDER BY date_registered DESC
"""