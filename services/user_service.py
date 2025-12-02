# services/user_service.py
from database.connection import db
from utils.security import hash_password, verify_password
import logging
from database.connection import db
from database.queries.users import *
from database.queries.analytics import *
import bcrypt


logger = logging.getLogger(__name__)


class UserService:
    def __init__(self):
        self.db = db

    def authenticate_user(self, email, password):
        """Аутентификация пользователя по email и паролю"""
        try:
            result = self.db.execute_query(
                "SELECT user_id, username, email, password_hash, role_id FROM users WHERE email = %s",
                (email,),
                fetch_one=True
            )

            if result and verify_password(password, result['password_hash']):
                return {
                    'user_id': result['user_id'],
                    'username': result['username'],
                    'email': result['email'],
                    'role_id': result['role_id']
                }
            return None

        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None

    def create_user(self, user_data):
        """Создание нового пользователя с никнеймом"""
        try:
            # Проверяем обязательные поля
            required_fields = ['username', 'email', 'password']
            for field in required_fields:
                if not user_data.get(field):
                    return None

            # Проверяем уникальность username и email
            existing_user = self.db.execute_query(
                "SELECT user_id FROM users WHERE username = %s OR email = %s",
                (user_data['username'], user_data['email']),
                fetch_one=True
            )

            if existing_user:
                return None

            # Хешируем пароль
            hashed_password = hash_password(user_data['password'])

            # Создаем пользователя
            user_id = self.db.execute_query(
                "INSERT INTO users (username, email, password_hash, first_name, last_name, role_id) VALUES (%s, %s, %s, %s, %s, 1) RETURNING user_id",
                (
                    user_data['username'],
                    user_data['email'],
                    hashed_password,
                    user_data.get('first_name', ''),
                    user_data.get('last_name', '')
                )
            )

            # Создаем плейлист "Избранное" для нового пользователя
            if user_id:
                self.db.execute_query(
                    "INSERT INTO playlists (user_id, playlist_title, is_favorite_playlist) VALUES (%s, 'Избранное', true)",
                    (user_id,)
                )

            return user_id

        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    def get_user_profile(self, user_id):
        """Получить профиль пользователя"""
        try:
            result = self.db.execute_query(
                "SELECT user_id, username, email, first_name, last_name, avatar_url, date_registered FROM users WHERE user_id = %s",
                (user_id,),
                fetch_one=True
            )
            return result if result else {}
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return {}

    # ЗАМЕНИТЬ методы get_user_stats и get_user_top_genres:

    def get_user_stats(self, user_id):
        """Получить статистику пользователя - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            # Статистика прослушиваний - используем правильные названия таблиц и полей
            listen_stats = self.db.execute_query(
                """
                SELECT 
                    COUNT(DISTINCT track_id) as unique_tracks,
                    COUNT(*) as total_listens,
                    COALESCE(SUM(listen_duration_ms), 0) as total_seconds
                FROM listening_history
                WHERE user_id = %s
                """,
                (user_id,),
                fetch_one=True
            )

            # Количество плейлистов
            playlist_count = self.db.execute_query(
                "SELECT COUNT(*) as count FROM playlists WHERE user_id = %s",
                (user_id,),
                fetch_one=True
            )

            stats = listen_stats if listen_stats else {'unique_tracks': 0, 'total_listens': 0, 'total_seconds': 0}
            stats['playlist_count'] = playlist_count['count'] if playlist_count else 0

            # Конвертируем миллисекунды в часы и минуты
            if stats['total_seconds']:
                total_seconds = stats['total_seconds'] // 1000  # конвертируем мс в секунды
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                stats['total_time'] = f"{hours}ч {minutes}м"
                stats['total_listens'] = stats['total_listens'] or 0
            else:
                stats['total_time'] = "0ч 0м"
                stats['total_listens'] = 0

            return stats

        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {'unique_tracks': 0, 'total_listens': 0, 'total_seconds': 0, 'playlist_count': 0,
                    'total_time': '0ч 0м'}

    def get_user_top_genres(self, user_id, limit=5):
        """Получить топ жанров пользователя - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            results = self.db.execute_query(
                """
                SELECT g.genre_name, COUNT(*) as listen_count
                FROM listening_history lh  
                JOIN tracks t ON lh.track_id = t.track_id
                JOIN track_genres tg ON t.track_id = tg.track_id 
                JOIN genres g ON tg.genre_id = g.genre_id
                WHERE lh.user_id = %s
                GROUP BY g.genre_id, g.genre_name
                ORDER BY listen_count DESC
                LIMIT %s
                """,
                (user_id, limit),
                fetch=True
            )
            return results if results else []
        except Exception as e:
            logger.error(f"Error getting user top genres: {e}")
            return []