# services/music_service.py
from database.connection import db
from database.queries import tracks as track_queries
from database.queries import favorites as favorite_queries
import logging
from database.queries import playlists as playlist_queries

logger = logging.getLogger(__name__)


class MusicService:
    def __init__(self):
        self.db = db

    def create_playlist(self, user_id, title, description=""):
        """Создать плейлист"""
        try:
            if not title or len(title.strip()) == 0:
                return None

            # Создаем плейлист
            result = self.db.execute_query(
                favorite_queries.CREATE_PLAYLIST,
                (user_id, title.strip(), description.strip())
            )

            # Получаем ID созданного плейлиста
            if result:
                playlist_result = self.db.execute_query(
                    "SELECT playlist_id FROM playlists WHERE user_id = %s AND playlist_title = %s ORDER BY date_created DESC LIMIT 1",
                    (user_id, title.strip()),
                    fetch_one=True
                )
                return playlist_result['playlist_id'] if playlist_result else None

            return None

        except Exception as e:
            logger.error(f"Error creating playlist: {e}")
            return None

    def search_tracks(self, query, limit=20, offset=0):
        """Поиск треков в базе"""
        try:
            if not query or len(query.strip()) == 0:
                return self.get_popular_tracks(limit, offset)

            search_pattern = f"%{query.strip()}%"

            results = self.db.execute_query(
                track_queries.SEARCH_TRACKS,
                (search_pattern, search_pattern, search_pattern,
                 search_pattern, search_pattern, limit, offset),
                fetch=True
            )

            return results if results else []

        except Exception as e:
            logger.error(f"Error searching tracks: {e}")
            return []

    def get_popular_tracks(self, limit=20, offset=0):
        """Получить популярные треки"""
        try:
            results = self.db.execute_query(
                track_queries.GET_POPULAR_TRACKS,
                (limit, offset),
                fetch=True
            )

            return results if results else []

        except Exception as e:
            logger.error(f"Error getting popular tracks: {e}")
            return self._get_fallback_tracks()

    def get_track_details(self, track_id):
        """Получить детальную информацию о треке"""
        try:
            result = self.db.execute_query(
                track_queries.GET_TRACK_DETAILS,
                (track_id,),
                fetch_one=True
            )

            return result if result else {}

        except Exception as e:
            logger.error(f"Error getting track details: {e}")
            return {}

    def toggle_favorite_track(self, user_id, track_id):
        """Добавить/удалить из избранного"""
        try:
            # Проверяем, есть ли уже в избранном
            existing = self.db.execute_query(
                favorite_queries.CHECK_FAVORITE,
                (user_id, track_id),
                fetch_one=True
            )

            if existing:
                # Удаляем из избранного
                result = self.db.execute_query(
                    favorite_queries.REMOVE_FROM_FAVORITES,
                    (user_id, track_id)
                )
                return result is not None
            else:
                # Добавляем в избранное
                result = self.db.execute_query(
                    favorite_queries.ADD_TO_FAVORITES,
                    (user_id, track_id)
                )
                return result is not None

        except Exception as e:
            logger.error(f"Error toggling favorite track: {e}")
            return False

    def get_user_favorites(self, user_id, limit=20, offset=0):
        """Получить избранные треки пользователя"""
        try:
            results = self.db.execute_query(
                favorite_queries.GET_USER_FAVORITES,
                (user_id, limit, offset),
                fetch=True
            )

            return results if results else []

        except Exception as e:
            logger.error(f"Error getting user favorites: {e}")
            return []

    def get_user_playlists(self, user_id):
        """Получить плейлисты пользователя"""
        try:
            results = self.db.execute_query(
                favorite_queries.GET_USER_PLAYLISTS,
                (user_id,),
                fetch=True
            )

            return results if results else []

        except Exception as e:
            logger.error(f"Error getting user playlists: {e}")
            return []

    # ИСПРАВИТЬ метод log_listen:
    def log_listen(self, user_id, track_id, duration_ms):  # duration_ms вместо duration
        """Записать прослушивание - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            result = self.db.execute_query(
                "INSERT INTO listening_history (user_id, track_id, listen_duration_ms) VALUES (%s, %s, %s)",
                (user_id, track_id, duration_ms)  # listen_duration_ms вместо listen_duration_seconds
            )
            return result is not None
        except Exception as e:
            logger.error(f"Error logging listen: {e}")
            return False

    # ДОБАВИТЬ новые методы:
    def get_user_top_artists(self, user_id, limit=10):
        """Получить топ исполнителей пользователя"""
        try:
            results = self.db.execute_query(
                """
                SELECT 
                    a.artist_name, 
                    COUNT(*) as listen_count
                FROM listening_history lh
                JOIN tracks t ON lh.track_id = t.track_id
                JOIN artists a ON t.artist_id = a.artist_id
                WHERE lh.user_id = %s
                GROUP BY a.artist_id, a.artist_name
                ORDER BY listen_count DESC
                LIMIT %s
                """,
                (user_id, limit),
                fetch=True
            )
            return results if results else []
        except Exception as e:
            logger.error(f"Error getting user top artists: {e}")
            return []

    def get_listening_history(self, user_id, limit=20):
        """Получить историю прослушиваний"""
        try:
            results = self.db.execute_query(
                """
                SELECT 
                    lh.listened_at,
                    t.track_name,
                    a.artist_name,
                    al.album_name,
                    lh.listen_duration_ms,
                    lh.completion_percentage
                FROM listening_history lh
                JOIN tracks t ON lh.track_id = t.track_id
                JOIN artists a ON t.artist_id = a.artist_id
                JOIN albums al ON t.album_id = al.album_id
                WHERE lh.user_id = %s
                ORDER BY lh.listened_at DESC
                LIMIT %s
                """,
                (user_id, limit),
                fetch=True
            )
            return results if results else []
        except Exception as e:
            logger.error(f"Error getting listening history: {e}")
            return []

    def _get_fallback_tracks(self):
        """Fallback данные если база пустая"""
        return [
            {
                'track_id': 1,
                'track_title': 'Bohemian Rhapsody',
                'artist_name': 'Queen',
                'album_title': 'A Night at the Opera',
                'cover_medium': 'https://via.placeholder.com/300',
                'cover_big': 'https://via.placeholder.com/600',
                'preview_url': 'https://www.soundjay.com/button/button-1.mp3',
                'duration_seconds': 355,
                'popularity_rank': 100,
                'genre_name': 'Rock',
                'release_date': '1975-10-31'
            },
            {
                'track_id': 2,
                'track_title': 'Blinding Lights',
                'artist_name': 'The Weeknd',
                'album_title': 'After Hours',
                'cover_medium': 'https://via.placeholder.com/300',
                'cover_big': 'https://via.placeholder.com/600',
                'preview_url': 'https://www.soundjay.com/button/button-2.mp3',
                'duration_seconds': 200,
                'popularity_rank': 95,
                'genre_name': 'Pop',
                'release_date': '2020-03-20'
            }
        ]