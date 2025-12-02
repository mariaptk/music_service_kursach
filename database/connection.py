# database/connection.py
import psycopg2
import psycopg2.extras
from config import config
import logging
import sys

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Класс для работы с базой данных PostgreSQL"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Инициализация подключения"""
        self.connection_params = {
            'host': config.DB_HOST,
            'port': config.DB_PORT,
            'database': config.DB_NAME,
            'user': config.DB_USER,
            'password': config.DB_PASSWORD
        }
        logger.info("Database connection initialized")

    def get_connection(self):
        """Получить соединение с базой данных"""
        try:
            conn = psycopg2.connect(
                **self.connection_params,
                cursor_factory=psycopg2.extras.DictCursor
            )
            logger.debug("Database connection established")
            return conn
        except psycopg2.OperationalError as e:
            logger.error(f"Database connection failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during connection: {e}")
            return None

    def execute_query(self, query, params=None, fetch=False, fetch_one=False):
        """
        Выполнить SQL запрос

        Args:
            query (str): SQL запрос
            params (tuple): Параметры для запроса
            fetch (bool): Возвращать ли результаты
            fetch_one (bool): Возвращать только одну запись

        Returns:
            Результаты запроса или количество affected rows
        """
        conn = self.get_connection()
        if not conn:
            logger.error("No database connection available")
            return None

        try:
            with conn.cursor() as cur:
                logger.debug(f"Executing query: {query[:100]}...")
                cur.execute(query, params or ())

                if fetch_one:
                    result = cur.fetchone()
                    return dict(result) if result else None
                elif fetch:
                    results = cur.fetchall()
                    return [dict(row) for row in results]
                else:
                    conn.commit()
                    # Для INSERT возвращаем ID новой записи
                    if query.strip().upper().startswith('INSERT'):
                        if cur.rowcount > 0 and 'RETURNING' in query.upper():
                            return cur.fetchone()[0]
                    return cur.rowcount

        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            conn.rollback()
            return None
        except Exception as e:
            logger.error(f"Unexpected error during query execution: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def execute_many(self, query, params_list):
        """Выполнить один запрос с множеством параметров"""
        conn = self.get_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.executemany(query, params_list)
                conn.commit()
                return cur.rowcount
        except psycopg2.Error as e:
            logger.error(f"Database error in execute_many: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    def check_connection(self):
        """Проверить подключение к базе данных"""
        conn = self.get_connection()
        if conn:
            conn.close()
            return True
        return False


# Создаем глобальный экземпляр для использования во всем приложении
db = DatabaseConnection()