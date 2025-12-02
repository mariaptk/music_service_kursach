# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database.connection import db
from services.user_service import UserService
from services.music_service import MusicService
from utils.security import login_required, admin_required
from database.queries.tracks import GET_TRACKS_FOR_CATALOG, SEARCH_TRACKS_FOR_CATALOG
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Замените на свой секретный ключ

# Инициализация сервисов
user_service = UserService()
music_service = MusicService()


# Главная страница
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('catalog'))  # Перенаправляем в каталог вместо dashboard
    return render_template('index.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# app.py (обновляем маршрут регистрации)
# app.py
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа по email и паролю"""
    if request.method == 'POST':
        email = request.form.get('email')  # Теперь используем email
        password = request.form.get('password')

        user = user_service.authenticate_user(email, password)
        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']  # Сохраняем username в сессии
            session['email'] = user['email']
            session['role_id'] = user['role_id']
            flash('Успешный вход в систему!', 'success')
            return redirect(url_for('catalog'))
        else:
            flash('Неверный email или пароль', 'error')

    return render_template('auth/login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации с никнеймом"""
    if request.method == 'POST':
        username = request.form.get('username')  # Никнейм
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')

        # Валидация
        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Пароль должен содержать минимум 6 символов', 'error')
            return render_template('auth/register.html')

        if len(username) < 3:
            flash('Никнейм должен содержать минимум 3 символа', 'error')
            return render_template('auth/register.html')

        if user_service.create_user({
            'username': username,
            'email': email,
            'password': password
        }):
            flash('Регистрация успешна! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Ошибка регистрации. Возможно, пользователь с таким email или никнеймом уже существует.', 'error')

    return render_template('auth/register.html')


@app.route('/profile')
@login_required
def profile():
    """Профиль пользователя с реальными данными"""
    user_profile = user_service.get_user_profile(session['user_id'])
    user_stats = user_service.get_user_stats(session['user_id'])
    top_genres = user_service.get_user_top_genres(session['user_id'])

    return render_template('user/profile.html',
                           user=user_profile,
                           stats=user_stats,
                           top_genres=top_genres)

@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))


# Пользовательские страницы
# app.py
@app.route('/catalog')
@login_required
def catalog():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '')
    genre_filter = request.args.get('genre', '')

    per_page = 6
    offset = (page - 1) * per_page

    try:
        if search_query:
            # Поиск треков
            tracks = db.execute_query(
                SEARCH_TRACKS_FOR_CATALOG,
                (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', per_page, offset)
            )
            # Получаем общее количество для пагинации
            count_query = """
            SELECT COUNT(*) 
            FROM tracks t
            JOIN artists a ON t.artist_id = a.artist_id
            JOIN albums al ON t.album_id = al.album_id
            WHERE t.track_title ILIKE %s OR a.artist_name ILIKE %s OR al.album_title ILIKE %s
            """
            total_count = \
            db.execute_query(count_query, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))[0][0]
        else:
            # Все треки
            tracks = db.execute_query(
                GET_TRACKS_FOR_CATALOG,
                (per_page, offset)
            )
            # Общее количество треков
            total_count = db.execute_query("SELECT COUNT(*) FROM tracks")[0][0]

        total_pages = (total_count + per_page - 1) // per_page

        # Преобразуем результат в список словарей для удобства
        tracks_list = []
        for track in tracks:
            tracks_list.append({
                'track_id': track['track_id'],
                'track_name': track['track_name'],
                'duration_ms': track['duration_ms'],  # duration_ms вместо duration_formatted
                'preview_url': track['preview_url'],
                'full_track_url': track['full_track_url'],
                'popularity': track['popularity'],
                'artist_name': track['artist_name'],
                'album_name': track['album_name'],
                'cover_url': track['cover_url']
            })

        return render_template('user/catalog.html',
                               tracks=tracks_list,
                               current_page=page,
                               total_pages=total_pages,
                               search_query=search_query,
                               genre_filter=genre_filter)

    except Exception as e:
        print(f"Error in catalog: {e}")
        return render_template('user/catalog.html',
                               tracks=[],
                               current_page=1,
                               total_pages=1,
                               search_query=search_query,
                               genre_filter=genre_filter)
@app.route('/library')
@login_required
def library():
    """Библиотека пользователя"""
    try:
        user_playlists = music_service.get_user_playlists(session['user_id'])
        favorite_tracks = music_service.get_favorite_tracks(session['user_id'])

        return render_template('user/library.html',
                               playlists=user_playlists or [],
                               favorite_tracks=favorite_tracks or [])

    except Exception as e:
        logger.error(f"Error in library: {e}")
        return render_template('user/library.html',
                               playlists=[],
                               favorite_tracks=[])


@app.route('/statistics')
@login_required
def statistics():
    """Статистика пользователя"""
    try:
        user_stats = user_service.get_user_stats(session['user_id'])
        top_genres = music_service.get_user_top_genres(session['user_id'])
        top_artists = music_service.get_user_top_artists(session['user_id'])
        listening_history = music_service.get_listening_history(session['user_id'], limit=20)

        return render_template('user/statistics.html',
                               user_stats=user_stats or {},
                               top_genres=top_genres or [],
                               top_artists=top_artists or [],
                               listening_history=listening_history or [])

    except Exception as e:
        logger.error(f"Error in statistics: {e}")
        return render_template('user/statistics.html',
                               user_stats={},
                               top_genres=[],
                               top_artists=[],
                               listening_history=[])


# app.py
@app.route('/api/favorites', methods=['POST'])
def add_to_favorites():
    """Добавить трек в избранное"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})

    data = request.get_json()
    track_id = data.get('track_id')

    if not track_id:
        return jsonify({'success': False, 'error': 'No track ID'})

    # Проверяем, не добавлен ли уже трек
    existing = db.execute_query(
        "SELECT 1 FROM favorite_tracks WHERE user_id = %s AND track_id = %s",
        (session['user_id'], track_id),
        fetch_one=True
    )

    if existing:
        return jsonify({'success': False, 'error': 'Already in favorites'})

    # Добавляем в избранное
    result = db.execute_query(
        "INSERT INTO favorite_tracks (user_id, track_id) VALUES (%s, %s)",
        (session['user_id'], track_id)
    )

    if result:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Database error'})

# API endpoints
@app.route('/api/track/<int:track_id>/play')
@login_required
def play_track(track_id):
    """Воспроизведение трека"""
    try:
        track = music_service.get_track_details(track_id)
        if track:
            # Логируем прослушивание
            music_service.log_listen(session['user_id'], track_id, 30)
            return jsonify({
                'success': True,
                'preview_url': track.get('preview_url', ''),
                'track_title': track.get('track_title', 'Unknown'),
                'artist_name': track.get('artist_name', 'Unknown')
            })
        return jsonify({'success': False, 'error': 'Track not found'})

    except Exception as e:
        logger.error(f"Error playing track: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'})


@app.route('/api/track/<int:track_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(track_id):
    """Добавление/удаление из избранного"""
    try:
        success = music_service.toggle_favorite_track(session['user_id'], track_id)
        return jsonify({'success': success})

    except Exception as e:
        logger.error(f"Error toggling favorite: {e}")
        return jsonify({'success': False})


@app.route('/api/playlist/create', methods=['POST'])
@login_required
def create_playlist():
    """Создание плейлиста"""
    try:
        title = request.json.get('title')
        description = request.json.get('description', '')

        playlist_id = music_service.create_playlist(
            session['user_id'],
            title,
            description
        )

        return jsonify({'success': bool(playlist_id), 'playlist_id': playlist_id})

    except Exception as e:
        logger.error(f"Error creating playlist: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'})


# Админ панель (временно закомментируем, если нет шаблонов)
"""
@app.route('/admin')
@admin_required
def admin_dashboard():
    stats = user_service.get_system_stats()
    return render_template('admin/dashboard.html', stats=stats)


@app.route('/admin/users')
@admin_required
def admin_users():
    users = user_service.get_all_users()
    return render_template('admin/users.html', users=users)


@app.route('/admin/tracks')
@admin_required
def admin_tracks():
    page = int(request.args.get('page', 1))
    limit = 20
    offset = (page - 1) * limit

    tracks = music_service.get_all_tracks(limit, offset)
    total_tracks = music_service.get_tracks_count()

    return render_template('admin/tracks.html',
                           tracks=tracks,
                           page=page,
                           total_tracks=total_tracks)
"""

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)