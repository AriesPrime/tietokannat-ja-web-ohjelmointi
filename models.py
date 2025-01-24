from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    attempt = db.Column(db.Integer, default=0)
    guesses = db.Column(db.String, default="")
    correct_word = db.Column(db.String(5), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    is_won = db.Column(db.Boolean, default=False)
    started_at = db.Column(db.DateTime, default=db.func.now())
    ended_at = db.Column(db.DateTime, nullable=True)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dark_mode = db.Column(db.Boolean, default=False)
    high_contrast = db.Column(db.Boolean, default=False)
    keyboard_only = db.Column(db.Boolean, default=False)

class GameStats(db.Model):
    __tablename__ = 'gamestats'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    games_played = db.Column(db.Integer, default=0)
    games_won = db.Column(db.Integer, default=0)
    total_attempts = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)

    def update_stats(self, game):
        self.games_played = self.games_played or 0
        self.games_won = self.games_won or 0
        self.total_attempts = self.total_attempts or 0
        self.longest_streak = self.longest_streak or 0
        self.current_streak = self.current_streak or 0

        self.games_played += 1
        self.total_attempts += game.attempt

        if game.is_won:
            self.games_won += 1
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        else:
            self.current_streak = 0


class Leaderboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(80), nullable=False)
    games_won = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float, default=0.0)
    average_attempts = db.Column(db.Float, default=0.0)

    def update_leaderboard(self, stats):
        self.games_won = stats.games_won
        self.longest_streak = stats.longest_streak
        self.win_rate = round(stats.games_won / stats.games_played, 2) if stats.games_played > 0 else 0.0
        self.average_attempts = round(stats.total_attempts / stats.games_played, 2) if stats.games_played > 0 else 0.0

class Distribution(db.Model):
    __tablename__ = 'distribution'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    one = db.Column(db.Integer, default=0)
    two = db.Column(db.Integer, default=0)
    three = db.Column(db.Integer, default=0)
    four = db.Column(db.Integer, default=0)
    five = db.Column(db.Integer, default=0)
    six = db.Column(db.Integer, default=0)

    def update_distribution(self, attempts):
        if attempts == 1:
            self.one += 1
        elif attempts == 2:
            self.two += 1
        elif attempts == 3:
            self.three += 1
        elif attempts == 4:
            self.four += 1
        elif attempts == 5:
            self.five += 1
        elif attempts == 6:
            self.six += 1
