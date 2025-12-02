# database/queries/favorites.py
"""SQL запросы для избранного и плейлистов"""

CREATE_PLAYLIST = """
INSERT INTO playlists (user_id, playlist_title, description)
VALUES (%s, %s, %s)
"""

# Остальные запросы остаются без изменений
CHECK_FAVORITE = """
SELECT 1 FROM favorite_tracks 
WHERE user_id = %s AND track_id = %s
"""

ADD_TO_FAVORITES = """
INSERT INTO favorite_tracks (user_id, track_id) 
VALUES (%s, %s)
ON CONFLICT (user_id, track_id) DO NOTHING
"""

REMOVE_FROM_FAVORITES = """
DELETE FROM favorite_tracks 
WHERE user_id = %s AND track_id = %s
"""