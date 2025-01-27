from db import db
from sqlalchemy.sql import text


def get_settings(user_id):
    sql = text("""
        SELECT dark_mode, high_contrast, keyboard_only
        FROM settings
        WHERE user_id = :user_id
    """)
    result = db.session.execute(sql, {"user_id": user_id}).fetchone()

    dark_mode, high_contrast, keyboard_only = result

    return {
        "dark_mode": dark_mode,
        "high_contrast": high_contrast,
        "keyboard_only": keyboard_only
    }


def set_settings(user_id, dark_mode, high_contrast, keyboard_only):
    try:
        sql = text("SELECT 1 FROM settings WHERE user_id = :user_id")
        result = db.session.execute(sql, {"user_id": user_id}).fetchone()

        sql = text("""
            INSERT INTO settings (user_id, dark_mode, high_contrast, keyboard_only)
            VALUES (:user_id, :dark_mode, :high_contrast, :keyboard_only)
        """)
        
        if result:
            sql = text("""
                UPDATE settings
                SET dark_mode = :dark_mode,
                    high_contrast = :high_contrast,
                    keyboard_only = :keyboard_only
                WHERE user_id = :user_id
            """)

        db.session.execute(sql, {
            "user_id": user_id,
            "dark_mode": dark_mode,
            "high_contrast": high_contrast,
            "keyboard_only": keyboard_only
        })
        db.session.commit()
        return True
    except:
        return False
