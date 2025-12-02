# utils/security.py
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string
from functools import wraps
from flask import session, redirect, url_for, flash

def hash_password(password):
    """Хешировать пароль"""
    return generate_password_hash(password)

def verify_password(password, password_hash):
    """Проверить пароль"""
    return check_password_hash(password_hash, password)

def generate_session_token(length=32):
    """Сгенерировать токен сессии"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему для доступа к этой странице.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему.', 'warning')
            return redirect(url_for('login'))
        if session.get('role_id') != 2:  # 2 = admin role
            flash('У вас нет прав для доступа к этой странице.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function