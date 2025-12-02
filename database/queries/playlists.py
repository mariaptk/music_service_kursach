# database/queries/playlists.py
# ЗАМЕНИТЬ СОДЕРЖИМОЕ ФАЙЛА:

# Плейлисты пользователя (ОБНОВЛЕНО)
GET_USER_PLAYLISTS = """
SELECT 
    playlist_id, 
    playlist_name, 
    description, 
    is_public, 
    date_created,
    (SELECT COUNT(*) FROM playlist_tracks WHERE playlist_id = playlists.playlist_id) as track_count
FROM playlists 
WHERE user_id = %s
ORDER BY date_created DESC
"""

# Создание плейлиста (ОБНОВЛЕНО)
CREATE_PLAYLIST = """
INSERT INTO playlists (user_id, playlist_name, description) 
VALUES (%s, %s, %s)
RETURNING playlist_id
"""

# Избранные треки (ОБНОВЛЕНО)
GET_FAVORITE_TRACKS = """
SELECT 
    t.track_id, 
    t.track_name, 
    t.duration_ms, 
    t.preview_url,
    t.full_track_url,
    a.artist_name,
    al.album_name,
    al.cover_url as cover_medium
FROM favorite_tracks ft
JOIN tracks t ON ft.track_id = t.track_id
JOIN artists a ON t.artist_id = a.artist_id
JOIN albums al ON t.album_id = al.album_id
WHERE ft.user_id = %s
ORDER BY ft.added_at DESC
LIMIT %s
"""