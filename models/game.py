from db import db
from sqlalchemy.sql import text

def new_game(user_id, correct_word):
    try:
        sql = text("""
            INSERT INTO games (user_id, attempt, guesses, correct_word, is_completed, is_won, started_at)
            VALUES (:user_id, 0, '', :correct_word, false, false, NOW())
            RETURNING id
        """)
        db.session.execute(sql, {"user_id": user_id, "correct_word": correct_word})
        db.session.commit()
        return True
    except:
        return False, None

def last_game(user_id):
    sql = text("""
        SELECT id, guesses, correct_word, is_completed, is_won
        FROM games
        WHERE user_id = :user_id
        ORDER BY id DESC
        LIMIT 1
    """)
    result = db.session.execute(sql, {"user_id": user_id}).fetchone()

    if result:
        return True, {
            "game_id": result[0],
            "guesses": result[1].split(",") if result[1] else [],
            "correct_word": result[2],
            "is_completed": result[3],
            "is_won": result[4],
        }
    
    return False, None
        
def save_guess(user_id, guess):
    try:
        sql = text("""
            SELECT id, guesses, correct_word
            FROM games
            WHERE user_id = :user_id AND is_completed = FALSE
            ORDER BY id DESC
            LIMIT 1
        """)
        game_id, previous_guesses, correct_word = db.session.execute(sql, {"user_id": user_id}).fetchone()

        guesses = previous_guesses.split(",") if previous_guesses else []
        guesses.append(guess)
        is_correct = guess == correct_word
        is_completed = is_correct or len(guesses) >= 6

        sql = text("""
            UPDATE games
            SET guesses = :guesses,
                is_completed = :is_completed,
                is_won = :is_won,
                ended_at = CASE WHEN :is_completed THEN NOW() ELSE NULL END
            WHERE id = :game_id
        """)
        db.session.execute(sql, {
            "guesses": ",".join(guesses),
            "is_completed": is_completed,
            "is_won": is_correct,
            "game_id": game_id,
        })
        db.session.commit()

        return True, {
            "game_over": is_completed,
            "is_won": is_correct,
            "guess_count": len(guesses),
        }
    except:
        return False, None