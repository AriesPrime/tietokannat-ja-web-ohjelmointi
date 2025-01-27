from db import db
from sqlalchemy.sql import text

def update_leaderboard(user_id, stats):
    sql = text("SELECT 1 FROM leaderboard WHERE user_id = :user_id")
    result = db.session.execute(sql, {"user_id": user_id}).fetchone()

    games_played = int(stats["games_played"])
    games_won = int(stats["games_won"])
    win_rate = float(stats["win_rate"])
    total_attempts = int(stats["total_attempts"])
    longest_streak = int(stats["longest_streak"])

    average_attempts = round(total_attempts / games_played, 1) if games_played > 0 else 0

    sql = text("""
        INSERT INTO leaderboard (user_id, username, games_won, longest_streak, win_rate, average_attempts)
        VALUES (:user_id, (SELECT username FROM users WHERE id = :user_id), :games_won, :longest_streak, :win_rate, :average_attempts)
    """)
    
    if result:
        sql = text("""
            UPDATE leaderboard
            SET games_won = :games_won,
                longest_streak = :longest_streak,
                win_rate = :win_rate,
                average_attempts = :average_attempts
            WHERE user_id = :user_id
        """)

    db.session.execute(sql, {
        "user_id": user_id,
        "games_won": games_won,
        "longest_streak": longest_streak,
        "win_rate": win_rate,
        "average_attempts": average_attempts,
    })
    db.session.commit()