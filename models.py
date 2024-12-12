from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class GameState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    attempt = db.Column(db.Integer, default=0)
    guesses = db.Column(db.JSON, default=list)
    correct_word = db.Column(db.String(5), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    is_won = db.Column(db.Boolean, default=False)
    started_at = db.Column(db.DateTime, default=db.func.now())
    ended_at = db.Column(db.DateTime)

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dark_mode = db.Column(db.Boolean, default=False)
    high_contrast = db.Column(db.Boolean, default=False)
    language = db.Column(db.String(50), default='English')

class Leaderboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    games_won = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)

class Guess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game_state.id'), nullable=False)
    guess = db.Column(db.String(5), nullable=False)
    attempt = db.Column(db.Integer, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)