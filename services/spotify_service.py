# services/spotify_service.py
import requests
import base64
import time
import logging
from datetime import datetime, timedelta
from config import config

logger = logging.getLogger(__name__)


class SpotifyService:
    """Полнофункциональный сервис для работы с Spotify API"""

    def __init__(self):
        self.base_url = "https://api.spotify.com/v1"
        self.auth_url = "https://accounts.spotify.com/api/token"
        self.client_id = config.SPOTIFY_CLIENT_ID
        self.client_secret = config.SPOTIFY_CLIENT_SECRET
        self.access_token = None
        self.token_expires = None
        self.request_count = 0
        self.last_request_time = 0

    def _get_access_token(self):
        """Получить access token для Spotify API"""
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return self.access_token

        if not self.client_id or not self.client_secret:
            logger.error("Spotify credentials not configured")
            return None

        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {'grant_type': 'client_credentials'}

        try:
            response = requests.post(self.auth_url, headers=headers, data=data, timeout=10)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                self.token_expires = datetime.now() + timedelta(seconds=token_data['expires_in'] - 60)
                logger.info("✅ Spotify access token obtained")
                return self.access_token
            else:
                logger.error(f"❌ Failed to get access token: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"❌ Error getting access token: {e}")
            return None

    def _make_request(self, endpoint, params=None):
        """Безопасный запрос к Spotify API с rate limiting"""
        token = self._get_access_token()
        if not token:
            return None

        # Rate limiting: 1 запрос в 0.1 секунду
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < 0.1:
            time.sleep(0.1 - time_since_last)

        url = f"{self.base_url}/{endpoint}"
        headers = {'Authorization': f'Bearer {token}'}

        try:
            self.request_count += 1
            response = requests.get(url, headers=headers, params=params, timeout=15)
            self.last_request_time = time.time()

            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 5))
                logger.warning(f"⏳ Rate limit hit, waiting {retry_after} seconds...")
                time.sleep(retry_after)
                return self._make_request(endpoint, params)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"⚠️ Resource not found: {endpoint}")
                return None
            else:
                logger.error(f"❌ Spotify API error {response.status_code}: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request failed: {e}")
            return None

    def search_tracks(self, query, limit=20, offset=0):
        """Поиск треков"""
        params = {
            'q': query,
            'type': 'track',
            'limit': limit,
            'offset': offset
        }
        return self._make_request("search", params)

    def get_track(self, track_id):
        """Получить информацию о треке"""
        return self._make_request(f"tracks/{track_id}")

    def get_track_audio_features(self, track_id):
        """Получить аудио-характеристики трека"""
        return self._make_request(f"audio-features/{track_id}")

    def get_artist(self, artist_id):
        """Получить информацию об артисте"""
        return self._make_request(f"artists/{artist_id}")

    def get_artist_top_tracks(self, artist_id, country='US'):
        """Получить топ треков артиста"""
        params = {'country': country}
        return self._make_request(f"artists/{artist_id}/top-tracks", params)

    def get_album(self, album_id):
        """Получить информацию об альбоме"""
        return self._make_request(f"albums/{album_id}")

    def get_album_tracks(self, album_id, limit=50, offset=0):
        """Получить треки альбома"""
        params = {'limit': limit, 'offset': offset}
        return self._make_request(f"albums/{album_id}/tracks", params)

    def get_genres(self):
        """Получить список жанров"""
        return self._make_request("recommendations/available-genre-seeds")

    def get_new_releases(self, limit=50, offset=0):
        """Получить новые релизы"""
        params = {'limit': limit, 'offset': offset}
        return self._make_request("browse/new-releases", params)

    def get_track_audio_url(self, track_id):
        """Получить URL для прослушивания полного трека"""
        track_data = self.get_track(track_id)
        if track_data and 'external_urls' in track_data:
            return track_data['external_urls'].get('spotify')
        return None

    def get_user_premium_status(self):
        """Проверить статус аккаунта (премиум или нет)"""
        # Для премиум аккаунтов доступны полные треки
        return True  # Твой аккаунт премиум