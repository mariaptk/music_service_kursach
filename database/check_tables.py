# database/check_tables.py
from database.connection import db


def check_database_structure():
    """Проверить, что все таблицы существуют"""

    required_tables = [
        'user_roles', 'users', 'genres', 'artists', 'albums',
        'tracks', 'playlists', 'playlist_tracks', 'listen_history',
        'favorite_tracks', 'user_sessions', 'reports',
        'admin_actions', 'recommendation_cache', 'search_queries'
    ]

    existing_tables = db.execute_query("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """, fetch=True)

    existing_table_names = [table['table_name'] for table in existing_tables]

    print("📊 Database Structure Check:")
    print("=" * 50)

    missing_tables = []
    for table in required_tables:
        if table in existing_table_names:
            print(f"✅ {table}")
        else:
            print(f"❌ {table} - MISSING")
            missing_tables.append(table)

    if missing_tables:
        print(f"\n⚠️  Missing tables: {missing_tables}")
        return False
    else:
        print(f"\n🎉 All {len(required_tables)} tables are present!")
        return True


if __name__ == "__main__":
    check_database_structure()