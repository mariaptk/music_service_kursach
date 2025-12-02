# test_spotify_previews.py
from services.spotify_service import SpotifyService

spotify = SpotifyService()

# Тестовые треки которые точно должны иметь превью
test_tracks = [
    '11dFghVXANMlKmJXsNCbNl',  # The Weeknd - Blinding Lights
    '0VjIjW4GlUZAMYd2vXMi3b',  # Taylor Swift - Blank Space
    '3PhoLpVuITZKcymswpck5b',  # Ed Sheeran - Shape of You
    '5ZULALImTm80tzUbYQYM9d',  # Dua Lipa - Don't Start Now
]

for track_id in test_tracks:
    track = spotify.get_track(track_id)
    if track:
        print(f"🎵 {track['name']} by {track['artists'][0]['name']}")
        print(f"   Preview URL: {track.get('preview_url', 'NO PREVIEW')}")
        print()
    else:
        print(f"❌ Could not fetch track {track_id}")