# run.py
from database.connection import db
from services.data_populator import PremiumDataPopulator
import logging
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

def initialize_database():
    """Инициализация базы данных"""
    logger.info("🚀 Starting database initialization...")

    # Проверяем подключение к БД
    if not db.check_connection():
        logger.error("❌ Cannot connect to database. Please check your configuration.")
        return False

    # Наполняем премиум данными
    logger.info("🎵 Populating with PREMIUM Spotify data...")
    populator = PremiumDataPopulator()

    if populator.populate_premium_data():
        logger.info("✅ PREMIUM data population completed!")
        return True
    else:
        logger.error("❌ Premium data population failed!")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🎵 MUSIC SERVICE - PREMIUM DATA INITIALIZATION")
    print("=" * 60)

    if initialize_database():
        print("\n" + "=" * 60)
        print("✅ SUCCESS! Your database is ready with PREMIUM data!")
        print("=" * 60)
        print("👤 Admin: username='admin', password='admin123'")
        print("👥 Users: username='user1', password='password123'")
        print("🎵 Data: Real artists with FULL TRACKS from Spotify")
        print("🔊 Features: Full track playback for premium accounts")
        print("📊 Stats: User activity, playlists, listening history")
        print("=" * 60)
    else:
        print("\n❌ INITIALIZATION FAILED!")
        print("Please check your Spotify credentials in .env file")