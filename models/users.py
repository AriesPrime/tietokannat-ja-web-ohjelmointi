from db import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import text

class User:
    def __init__(self, id, username):
        self.id = id
        self.username = username

    def get_id(self):
        return str(self.id)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_active(self):
        return True

    @staticmethod
    def get_user_by_id(user_id):
        sql = text("SELECT id, username FROM users WHERE id=:id")
        result = db.session.execute(sql, {"id": user_id}).fetchone()
        return User(id=result[0], username=result[1]) if result else None

    @staticmethod
    def get_user_by_username(username):
        sql = text("SELECT id, username, password_hash FROM users WHERE username=:username")
        result = db.session.execute(sql, {"username": username}).fetchone()
        return {"id": result[0], "username": result[1], "password_hash": result[2]} if result else None

def signup(username, email, password):
    sql = text("SELECT 1 FROM users WHERE username=:username OR email=:email")

    if db.session.execute(sql, {"username": username, "email": email}).fetchone():
        return False, "Username or email already exists. Please choose another."
    
    password_hash = generate_password_hash(password)
    try:
        sql = text("""
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (:username, :email, :password_hash, NOW())
            RETURNING id
        """)
        user_id = db.session.execute(sql, {"username": username, "email": email, "password_hash": password_hash}).fetchone()[0]

        sql = text("""
            INSERT INTO settings (user_id, dark_mode, high_contrast, keyboard_only)
            VALUES (:user_id, False, False, False)
        """)
        db.session.execute(sql, {"user_id": user_id})

        sql = text("""
            INSERT INTO distributions (user_id, one, two, three, four, five, six)
            VALUES (:user_id, 0, 0, 0, 0, 0, 0)
        """)
        db.session.execute(sql, {"user_id": user_id})

        sql = text("""
            INSERT INTO gamestats (user_id, games_played, games_won, total_attempts, longest_streak, current_streak)
            VALUES (:user_id, 0, 0, 0, 0, 0)
        """)
        db.session.execute(sql, {"user_id": user_id})

        sql = text("""
            INSERT INTO leaderboard (user_id, username, games_won, longest_streak, win_rate, average_attempts)
            VALUES (:user_id, (SELECT username FROM users WHERE id = :user_id), 0, 0, 0, 0)
        """)
        db.session.execute(sql, {"user_id": user_id})

        db.session.commit()
    except:
        return False, "An error occurred during registration. Please try again."
    
    return True, None

def signin(username, password):
    user_data = User.get_user_by_username(username)
    if user_data and check_password_hash(user_data["password_hash"], password):
        return User(id=user_data["id"], username=user_data["username"])
    return None