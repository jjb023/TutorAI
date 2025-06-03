from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from utils.database import get_db_connection

class User(UserMixin):
    def __init__(self, id, username, password, is_admin=False):
        self.id = id
        self.username = username
        self.password = password
        self.is_admin = is_admin

    @staticmethod
    def get(user_id):
        """Get user by ID."""
        with get_db_connection() as conn:
            user = conn.execute(
                'SELECT * FROM users WHERE id = ?', (user_id,)
            ).fetchone()
            if user:
                return User(user['id'], user['username'], user['password'], user['is_admin'])
        return None

    @staticmethod
    def get_by_username(username):
        """Get user by username."""
        with get_db_connection() as conn:
            user = conn.execute(
                'SELECT * FROM users WHERE username = ?', (username,)
            ).fetchone()
            if user:
                return User(user['id'], user['username'], user['password'], user['is_admin'])
        return None

    def check_password(self, password):
        """Check if provided password matches user's password."""
        return check_password_hash(self.password, password)

    @staticmethod
    def create(username, password, is_admin=False):
        """Create a new user."""
        hashed_password = generate_password_hash(password)
        with get_db_connection() as conn:
            conn.execute(
                'INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                (username, hashed_password, is_admin)
            )
            conn.commit()

    def __repr__(self):
        return f'<User {self.username}>'