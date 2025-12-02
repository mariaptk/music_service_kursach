# ПОЛНОСТЬЮ ЗАМЕНИТЬ СОДЕРЖИМОЕ ФАЙЛА:

# Поиск треков (ОБНОВЛЕНО под вашу схему)
SEARCH_TRACKS = """
SELECT 
    t.track_id, 
    t.track_name, 
    t.duration_ms, 
    t.preview_url, 
    t.full_track_url,
    t.popularity_score as popularity,
    t.explicit,
    a.artist_name, 
    a.artist_id,
    al.album_name as album_title, 
    al.cover_url as cover_medium,
    EXISTS (
        SELECT 1 FROM favorite_tracks ft 
        WHERE ft.user_id = %s AND ft.track_id = t.track_id
    ) as is_favorite
FROM tracks t
JOIN artists a ON t.artist_id = a.artist_id
JOIN albums al ON t.album_id = al.album_id
WHERE t.track_name ILIKE %s OR a.artist_name ILIKE %s OR al.album_name ILIKE %s
ORDER BY t.popularity_score DESC
LIMIT %s OFFSET %s
"""

# Детали трека (ОБНОВЛЕНО)
GET_TRACK_BY_ID = """
SELECT 
    t.*,
    a.artist_name,
    al.album_name as album_title,
    al.cover_url as cover_large
FROM tracks t
JOIN artists a ON t.artist_id = a.artist_id
JOIN albums al ON t.album_id = al.album_id
WHERE t.track_id = %s
"""

# Популярные треки (ОБНОВЛЕНО)
GET_POPULAR_TRACKS = """
SELECT 
    t.track_id, 
    t.track_name as track_title, 
    t.duration_ms, 
    t.preview_url, 
    t.full_track_url,
    t.popularity_score as popularity,
    a.artist_name,
    al.album_name as album_title, 
    al.cover_url as cover_medium
FROM tracks t
JOIN artists a ON t.artist_id = a.artist_id
JOIN albums al ON t.album_id = al.album_id
ORDER BY t.popularity_score DESC
LIMIT %s
"""

# Все треки (админ) (ОБНОВЛЕНО)
GET_ALL_TRACKS = """
SELECT 
    t.track_id, 
    t.track_name as track_title, 
    t.popularity_score as popularity, 
    t.explicit, 
    t.full_track_url,
    a.artist_name,
    al.album_name as album_title
FROM tracks t
JOIN artists a ON t.artist_id = a.artist_id
JOIN albums al ON t.album_id = al.album_id
ORDER BY t.track_id
LIMIT %s OFFSET %s
"""

# Получить треки для каталога (ОБНОВЛЕНО)
GET_TRACKS_FOR_CATALOG = """
SELECT 
    t.track_id,
    t.track_name,
    t.duration_ms,
    t.preview_url,
    t.full_track_url,
    t.popularity_score as popularity,
    a.artist_name,
    al.album_name as album_name,
    al.cover_url as cover_url
FROM tracks t
JOIN artists a ON t.artist_id = a.artist_id
JOIN albums al ON t.album_id = al.album_id
ORDER BY t.popularity_score DESC
LIMIT %s OFFSET %s
"""

# Поиск треков для каталога (ОБНОВЛЕНО)
SEARCH_TRACKS_FOR_CATALOG = """
SELECT 
    t.track_id,
    t.track_name,
    t.duration_ms,
    t.preview_url,
    t.full_track_url,
    t.popularity_score as popularity,
    a.artist_name,
    al.album_name as album_name,
    al.cover_url as cover_url
FROM tracks t
JOIN artists a ON t.artist_id = a.artist_id
JOIN albums al ON t.album_id = al.album_id
WHERE t.track_name ILIKE %s OR a.artist_name ILIKE %s OR al.album_name ILIKE %s
ORDER BY t.popularity_score DESC
LIMIT %s OFFSET %s
"""