-- database/schema_optimized.sql
DROP TABLE IF EXISTS listening_history CASCADE;
DROP TABLE IF EXISTS playlist_tracks CASCADE;
DROP TABLE IF EXISTS favorite_tracks CASCADE;
DROP TABLE IF EXISTS track_genres CASCADE;
DROP TABLE IF EXISTS artist_genres CASCADE;
DROP TABLE IF EXISTS audio_features CASCADE;
DROP TABLE IF EXISTS tracks CASCADE;
DROP TABLE IF EXISTS albums CASCADE;
DROP TABLE IF EXISTS artists CASCADE;
DROP TABLE IF EXISTS genres CASCADE;
DROP TABLE IF EXISTS system_reports CASCADE;
DROP TABLE IF EXISTS admin_actions CASCADE;
DROP TABLE IF EXISTS user_actions CASCADE;
DROP TABLE IF EXISTS search_queries CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS playlists CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS user_roles CASCADE;

-- 1. Роли пользователей
CREATE TABLE user_roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    role_description TEXT
);

-- 2. Пользователи (добавили avatar_url)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    role_id INTEGER NOT NULL REFERENCES user_roles(role_id),
    avatar_url VARCHAR(500),
    date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 3. Жанры
CREATE TABLE genres (
    genre_id SERIAL PRIMARY KEY,
    genre_name VARCHAR(100) UNIQUE NOT NULL,
    spotify_genre_id VARCHAR(100)
);

-- 4. Исполнители
CREATE TABLE artists (
    artist_id SERIAL PRIMARY KEY,
    spotify_artist_id VARCHAR(100) UNIQUE NOT NULL,
    artist_name VARCHAR(200) NOT NULL,
    popularity_score INTEGER DEFAULT 0,
    followers_count INTEGER DEFAULT 0,
    image_url VARCHAR(500)
);

-- 5. Альбомы
CREATE TABLE albums (
    album_id SERIAL PRIMARY KEY,
    spotify_album_id VARCHAR(100) UNIQUE NOT NULL,
    album_name VARCHAR(255) NOT NULL,
    artist_id INTEGER NOT NULL REFERENCES artists(artist_id),
    album_type VARCHAR(50) NOT NULL,
    total_tracks INTEGER DEFAULT 0,
    release_date DATE,
    release_date_precision VARCHAR(10),
    cover_url VARCHAR(500)
);

CREATE TABLE tracks (
    track_id SERIAL PRIMARY KEY,
    spotify_track_id VARCHAR(100) UNIQUE NOT NULL,
    track_name VARCHAR(255) NOT NULL,
    album_id INTEGER NOT NULL REFERENCES albums(album_id),
    duration_ms INTEGER NOT NULL,
    track_number INTEGER,
    disc_number INTEGER DEFAULT 1,
    explicit BOOLEAN DEFAULT FALSE,
    popularity_score INTEGER DEFAULT 0,
    preview_url VARCHAR(500),          -- 30-секундное превью
    full_track_url VARCHAR(500),       -- ПОЛНЫЙ ТРЕК для премиум аккаунта!
    external_url VARCHAR(500),
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Аудио-характеристики
CREATE TABLE audio_features (
    track_id INTEGER PRIMARY KEY REFERENCES tracks(track_id) ON DELETE CASCADE,
    danceability FLOAT,
    energy FLOAT,
    key INTEGER,
    loudness FLOAT,
    mode INTEGER,
    speechiness FLOAT,
    acousticness FLOAT,
    instrumentalness FLOAT,
    liveness FLOAT,
    valence FLOAT,
    tempo FLOAT,
    time_signature INTEGER
);

-- 8. Связь: треки и жанры
CREATE TABLE track_genres (
    track_id INTEGER REFERENCES tracks(track_id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES genres(genre_id) ON DELETE CASCADE,
    PRIMARY KEY (track_id, genre_id)
);

-- 9. Связь: артисты и жанры
CREATE TABLE artist_genres (
    artist_id INTEGER REFERENCES artists(artist_id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES genres(genre_id) ON DELETE CASCADE,
    PRIMARY KEY (artist_id, genre_id)
);

-- 10. Плейлисты (добавили cover_url)
CREATE TABLE playlists (
    playlist_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    playlist_name VARCHAR(255) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    is_favorite BOOLEAN DEFAULT FALSE,
    cover_url VARCHAR(500),
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. Треки в плейлистах
CREATE TABLE playlist_tracks (
    playlist_id INTEGER REFERENCES playlists(playlist_id) ON DELETE CASCADE,
    track_id INTEGER REFERENCES tracks(track_id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    track_order INTEGER NOT NULL,
    PRIMARY KEY (playlist_id, track_id)
);

-- 12. История прослушиваний
CREATE TABLE listening_history (
    listen_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    track_id INTEGER NOT NULL REFERENCES tracks(track_id) ON DELETE CASCADE,
    listened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    listen_duration_ms INTEGER NOT NULL,
    completion_percentage FLOAT
);

-- 13. Избранные треки
CREATE TABLE favorite_tracks (
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    track_id INTEGER REFERENCES tracks(track_id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, track_id)
);

-- 14. Сессии пользователей
CREATE TABLE user_sessions (
    session_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    ip_address VARCHAR(45)
);

-- 15. Поисковые запросы
CREATE TABLE search_queries (
    query_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    query_text VARCHAR(500) NOT NULL,
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 16. Действия пользователей
CREATE TABLE user_actions (
    action_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    action_type VARCHAR(100) NOT NULL,
    target_type VARCHAR(100),
    target_id INTEGER,
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 17. Действия администратора
CREATE TABLE admin_actions (
    action_id SERIAL PRIMARY KEY,
    admin_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    action_type VARCHAR(100) NOT NULL,
    target_type VARCHAR(100),
    target_id INTEGER,
    description TEXT,
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 18. Системные отчеты
CREATE TABLE system_reports (
    report_id SERIAL PRIMARY KEY,
    report_type VARCHAR(100) NOT NULL,
    generated_by_user_id INTEGER REFERENCES users(user_id),
    parameters JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ТОЛЬКО КРИТИЧЕСКИЕ ИНДЕКСЫ:
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_tracks_name ON tracks(track_name);
CREATE INDEX idx_artists_name ON artists(artist_name);
CREATE INDEX idx_albums_name ON albums(album_name);
CREATE INDEX idx_listening_history_user_date ON listening_history(user_id, listened_at);
CREATE INDEX idx_listening_history_track ON listening_history(track_id);
CREATE INDEX idx_playlists_user ON playlists(user_id);
CREATE INDEX idx_user_actions_user_date ON user_actions(user_id, performed_at);