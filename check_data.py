# check_data.py
from database.connection import db

# Проверим есть ли треки в базе
tracks_count = db.execute_query("SELECT COUNT(*) as count FROM tracks", fetch_one=True)
artists_count = db.execute_query("SELECT COUNT(*) as count FROM artists", fetch_one=True)
albums_count = db.execute_query("SELECT COUNT(*) as count FROM albums", fetch_one=True)

print(f"🎵 Треков в базе: {tracks_count['count'] if tracks_count else 0}")
print(f"🎤 Артистов в базе: {artists_count['count'] if artists_count else 0}")
print(f"💿 Альбомов в базе: {albums_count['count'] if albums_count else 0}")

# Покажем несколько треков если они есть
if tracks_count and tracks_count['count'] > 0:
    tracks = db.execute_query("""
        SELECT t.track_name, a.artist_name, al.album_name 
        FROM tracks t  
        JOIN albums al ON t.album_id = al.album_id
        JOIN artists a ON al.artist_id = a.artist_id 
        LIMIT 5
    """, fetch=True)

    print("\n📋 Примеры треков:")
    for track in tracks:
        print(f"  - {track['track_name']} by {track['artist_name']}")
else:
    print("\n❌ В базе нет треков! Нужно заполнить базу данных.")