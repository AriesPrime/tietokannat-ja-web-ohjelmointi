from db import db
from sqlalchemy.sql import text

def get_stats(user_id):
    sql = text("""
        SELECT games_played, games_won, total_attempts, longest_streak, current_streak
        FROM gamestats
        WHERE user_id = :user_id
    """)
    result = db.session.execute(sql, {"user_id": user_id}).fetchone()

    games_played, games_won, total_attempts, longest_streak, current_streak = result

    win_rate = round((games_won / games_played) * 100, 0) if games_played > 0 else 0

    return {
        "games_played": games_played,
        "games_won": games_won,
        "win_rate": win_rate,
        "total_attempts": total_attempts,
        "longest_streak": longest_streak,
        "current_streak": current_streak,
    }

def update_stats(user_id, game):
    sql = text("SELECT 1 FROM gamestats WHERE user_id = :user_id")
    result = db.session.execute(sql, {"user_id": user_id}).fetchone()

    stats = get_stats(user_id)
    total_attempts = stats["total_attempts"] + game["guess_count"]
    games_played = stats["games_played"] + 1
    games_won = stats["games_won"] + (1 if game["is_won"] else 0)
    current_streak = stats["current_streak"] + 1 if game["is_won"] else 0
    longest_streak = max(stats["longest_streak"], current_streak)


    sql = text("""
        INSERT INTO gamestats (user_id, games_played, games_won, total_attempts, longest_streak, current_streak)
        VALUES (:user_id, :games_played, :games_won, :total_attempts, :longest_streak, :current_streak)
    """)
    
    if result:
        sql = text("""
            UPDATE gamestats
            SET games_played = :games_played,
                games_won = :games_won,
                total_attempts = :total_attempts,
                longest_streak = :longest_streak,
                current_streak = :current_streak
            WHERE user_id = :user_id
        """)

    db.session.execute(sql, {
        "user_id": user_id,
        "games_played": games_played,
        "games_won": games_won,
        "total_attempts": total_attempts,
        "longest_streak": longest_streak,
        "current_streak": current_streak,
    })

    db.session.commit()