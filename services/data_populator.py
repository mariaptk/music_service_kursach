# services/data_populator.py
from database.connection import db
from services.spotify_service import SpotifyService
from utils.security import hash_password
import logging
import time
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PremiumDataPopulator:
    """Наполнение базы с полными треками для премиум аккаунта"""

    def __init__(self):
        self.db = db
        self.spotify = SpotifyService()
        self.processed_artists = set()
        self.processed_albums = set()
        self.processed_tracks = set()

    def populate_premium_data(self):
        """Наполнить базу полными треками"""
        logger.info("🎵 Starting PREMIUM data population from Spotify...")

        try:
            # 1. Базовые данные системы
            self._create_system_data()

            # 2. Получаем реальные жанры
            genre_ids = self._get_real_genres()

            # 3. Получаем популярных артистов с полными треками
            self._populate_premium_artists(genre_ids)

            # 4. Создаем пользовательскую активность
            self._create_user_activity()

            logger.info("✅ PREMIUM data population completed!")
            return True

        except Exception as e:
            logger.error(f"❌ Premium data population failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def _create_system_data(self):
        """Создать системные данные"""
        # Роли
        roles = [
            ('user', 'Обычный пользователь'),
            ('admin', 'Администратор системы'),
            ('moderator', 'Модератор контента')
        ]

        for role_name, description in roles:
            exists = self.db.execute_query(
                "SELECT role_id FROM user_roles WHERE role_name = %s",
                (role_name,),
                fetch_one=True
            )
            if not exists:
                self.db.execute_query(
                    "INSERT INTO user_roles (role_name, role_description) VALUES (%s, %s)",
                    (role_name, description)
                )

        # Администратор
        admin_password = hash_password("admin123")
        exists = self.db.execute_query(
            "SELECT user_id FROM users WHERE username = 'admin'",
            fetch_one=True
        )
        if not exists:
            self.db.execute_query(
                """INSERT INTO users (username, email, password_hash, first_name, last_name, role_id) 
                   VALUES (%s, %s, %s, %s, %s, 2)""",
                ('admin', 'admin@music-service.by', admin_password, 'Системный', 'Администратор')
            )

        # Тестовые пользователи
        test_users = [
            ('user1', 'user1@test.com', 'password123', 'Иван', 'Петров'),
            ('user2', 'user2@test.com', 'password123', 'Мария', 'Сидорова'),
            ('user3', 'user3@test.com', 'password123', 'Алексей', 'Козлов'),
        ]

        for username, email, password, first_name, last_name in test_users:
            exists = self.db.execute_query(
                "SELECT user_id FROM users WHERE username = %s",
                (username,),
                fetch_one=True
            )
            if not exists:
                hashed_password = hash_password(password)
                self.db.execute_query(
                    """INSERT INTO users (username, email, password_hash, first_name, last_name, role_id) 
                       VALUES (%s, %s, %s, %s, %s, 1)""",
                    (username, email, hashed_password, first_name, last_name)
                )

        logger.info("✅ System data created")

    def _get_real_genres(self):
        """Получить реальные жанры"""
        logger.info("🎶 Creating genres...")

        popular_genres = [
            'pop', 'rock', 'hip-hop', 'electronic', 'jazz', 'classical',
            'metal', 'r-n-b', 'country', 'reggae', 'blues', 'folk'
        ]

        genre_ids = []
        for genre_name in popular_genres:
            existing = self.db.execute_query(
                "SELECT genre_id FROM genres WHERE genre_name = %s",
                (genre_name,),
                fetch_one=True
            )

            if existing:
                genre_ids.append(existing['genre_id'])
            else:
                self.db.execute_query(
                    "INSERT INTO genres (genre_name) VALUES (%s)",
                    (genre_name,)
                )
                new_genre = self.db.execute_query(
                    "SELECT genre_id FROM genres WHERE genre_name = %s",
                    (genre_name,),
                    fetch_one=True
                )
                if new_genre:
                    genre_ids.append(new_genre['genre_id'])

        logger.info(f"✅ {len(genre_ids)} genres ready")
        return genre_ids

    def _populate_premium_artists(self, genre_ids):
        """Наполнить артистами с полными треками"""
        logger.info("🎤 Fetching premium artists with FULL TRACKS...")

        premium_artists = [
            'The Weeknd', 'Taylor Swift', 'Drake', 'Ed Sheeran',
            'Ariana Grande', 'Billie Eilish', 'Dua Lipa', 'Post Malone',
            'Coldplay', 'Bruno Mars', 'Harry Styles', 'Doja Cat'
        ]

        successful_artists = 0

        for artist_name in premium_artists:
            if successful_artists >= 8:  # Ограничим для теста
                break

            logger.info(f"🔍 Searching FULL TRACKS for: {artist_name}")

            # Ищем артиста
            search_results = self.spotify.search_tracks(f'artist:"{artist_name}"', limit=5)

            if not search_results or 'tracks' not in search_results:
                logger.warning(f"⚠️ No results for: {artist_name}")
                continue

            tracks = search_results['tracks'].get('items', [])
            if not tracks:
                logger.warning(f"⚠️ No tracks found for: {artist_name}")
                continue

            # Берем первого артиста
            first_track = tracks[0]
            if not first_track.get('artists'):
                continue

            artist_data = first_track['artists'][0]
            artist_id = artist_data['id']

            if artist_id in self.processed_artists:
                continue

            # Обрабатываем артиста
            if self._process_premium_artist(artist_id, genre_ids, artist_name):
                successful_artists += 1
                logger.info(f"✅ Processed with FULL TRACKS: {artist_name}")

            time.sleep(0.5)

        logger.info(f"🎉 Processed {successful_artists} artists with full tracks")

    def _process_premium_artist(self, artist_id, genre_ids, artist_name):
        """Обработать артиста с полными треками"""
        artist_data = self.spotify.get_artist(artist_id)
        if not artist_data:
            return False

        try:
            # Вставляем артиста
            self.db.execute_query(
                """INSERT INTO artists (spotify_artist_id, artist_name, popularity_score, followers_count, image_url) 
                   VALUES (%s, %s, %s, %s, %s)""",
                (
                    artist_data['id'],
                    artist_data['name'],
                    artist_data.get('popularity', 0),
                    artist_data.get('followers', {}).get('count', 0),
                    artist_data['images'][0]['url'] if artist_data.get('images') else None
                )
            )

            # Получаем ID артиста
            new_artist = self.db.execute_query(
                "SELECT artist_id FROM artists WHERE spotify_artist_id = %s",
                (artist_data['id'],),
                fetch_one=True
            )

            if not new_artist:
                return False

            artist_db_id = new_artist['artist_id']
            self.processed_artists.add(artist_id)

            # Получаем топ треки артиста
            top_tracks = self.spotify.get_artist_top_tracks(artist_id)
            if top_tracks and 'tracks' in top_tracks:
                for track in top_tracks['tracks']:
                    self._process_premium_track(track, artist_db_id, genre_ids)
                    time.sleep(0.3)

            return True

        except Exception as e:
            logger.error(f"❌ Error processing premium artist {artist_name}: {e}")
            return False

    def _process_premium_track(self, track_data, artist_db_id, genre_ids):
        """Обработать трек с полной версией"""
        if not track_data or 'id' not in track_data:
            return

        if track_data['id'] in self.processed_tracks:
            return

        try:
            # Обрабатываем альбом
            album_db_id = self._process_premium_album(track_data.get('album'), artist_db_id)
            if not album_db_id:
                return

            # Получаем URL для полного трека (Spotify URI)
            full_track_url = f"spotify:track:{track_data['id']}"

            # Вставляем трек с полной версией
            self.db.execute_query(
                """INSERT INTO tracks (spotify_track_id, track_name, album_id, duration_ms, 
                                    track_number, disc_number, explicit, popularity_score, 
                                    preview_url, full_track_url, external_url) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    track_data['id'],
                    track_data['name'],
                    album_db_id,
                    track_data['duration_ms'],
                    track_data.get('track_number', 1),
                    track_data.get('disc_number', 1),
                    track_data.get('explicit', False),
                    track_data.get('popularity', 0),
                    track_data.get('preview_url'),
                    full_track_url,  # 🔥 ПОЛНЫЙ ТРЕК!
                    track_data.get('external_urls', {}).get('spotify')
                )
            )

            self.processed_tracks.add(track_data['id'])
            logger.info(f"✅ FULL TRACK: {track_data['name']}")

        except Exception as e:
            logger.error(f"❌ Error processing premium track {track_data.get('name')}: {e}")

    def _process_premium_album(self, album_data, artist_db_id):
        """Обработать альбом"""
        if not album_data or 'id' not in album_data:
            return None

        if album_data['id'] in self.processed_albums:
            existing = self.db.execute_query(
                "SELECT album_id FROM albums WHERE spotify_album_id = %s",
                (album_data['id'],),
                fetch_one=True
            )
            return existing['album_id'] if existing else None

        try:
            # Вставляем альбом
            self.db.execute_query(
                """INSERT INTO albums (spotify_album_id, album_name, artist_id, album_type, 
                                    total_tracks, release_date, release_date_precision, cover_url) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    album_data['id'],
                    album_data['name'],
                    artist_db_id,
                    album_data['album_type'],
                    album_data.get('total_tracks', 0),
                    album_data.get('release_date'),
                    album_data.get('release_date_precision', 'day'),
                    album_data['images'][0]['url'] if album_data.get('images') else None
                )
            )

            # Получаем ID альбома
            new_album = self.db.execute_query(
                "SELECT album_id FROM albums WHERE spotify_album_id = %s",
                (album_data['id'],),
                fetch_one=True
            )

            if new_album:
                self.processed_albums.add(album_data['id'])
                return new_album['album_id']

            return None

        except Exception as e:
            logger.error(f"❌ Error processing album {album_data.get('name')}: {e}")
            return None

    def _create_user_activity(self):
        """Создать пользовательскую активность"""
        logger.info("👥 Creating user activity...")

        # Получаем пользователей
        users = self.db.execute_query("SELECT user_id FROM users WHERE role_id = 1", fetch=True)
        if not users:
            return

        # Получаем треки
        tracks = self.db.execute_query("SELECT track_id, duration_ms FROM tracks", fetch=True)
        if not tracks:
            return

        # Создаем плейлисты и историю прослушиваний
        for user in users:
            user_id = user['user_id']

            # Плейлист "Избранное"
            self.db.execute_query(
                """INSERT INTO playlists (user_id, playlist_name, is_favorite, description) 
                   VALUES (%s, %s, %s, %s)""",
                (user_id, 'Избранное', True, 'Мои любимые треки')
            )

            # Добавляем несколько треков в избранное
            if tracks:
                favorite_tracks = tracks[:5]  # Первые 5 треков
                for i, track in enumerate(favorite_tracks):
                    self.db.execute_query(
                        "INSERT INTO favorite_tracks (user_id, track_id) VALUES (%s, %s)",
                        (user_id, track['track_id'])
                    )

        logger.info("✅ User activity created")