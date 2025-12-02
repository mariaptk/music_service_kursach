# database/queries/analytics.py
# Топ жанров пользователя
USER_TOP_GENRES = """
SELECT 
    g.genre_name,
    COUNT(*) as listen_count,
    COUNT(DISTINCT lh.track_id) as unique_tracks
FROM listen_history lh
JOIN tracks t ON lh.track_id = t.track_id
JOIN artists a ON t.artist_id = a.artist_id
JOIN artist_genres ag ON a.artist_id = ag.artist_id
JOIN genres g ON ag.genre_id = g.genre_id
WHERE lh.user_id = %s
GROUP BY g.genre_id, g.genre_name
ORDER BY listen_count DESC
LIMIT 10
"""

# Топ артистов пользователя
USER_TOP_ARTISTS = """
SELECT 
    a.artist_name,
    COUNT(*) as listen_count,
    COUNT(DISTINCT lh.track_id) as unique_tracks
FROM listen_history lh
JOIN tracks t ON lh.track_id = t.track_id
JOIN artists a ON t.artist_id = a.artist_id
WHERE lh.user_id = %s
GROUP BY a.artist_id, a.artist_name
ORDER BY listen_count DESC
LIMIT 10
"""

# История прослушиваний
USER_LISTENING_HISTORY = """
SELECT 
    lh.listened_at,
    t.track_name as track_title,  
    al.album_name as album_title,  
    lh.completion_percentage
FROM listening_history lh
JOIN tracks t ON lh.track_id = t.track_id
JOIN artists a ON t.artist_id = a.artist_id  
JOIN albums al ON t.album_id = al.album_id
WHERE lh.user_id = %s
ORDER BY lh.listened_at DESC
LIMIT %s
"""