from db import db
from sqlalchemy.sql import text

def update_distribution(user_id, attempts):
    column_mapping = {
        1: "one",
        2: "two",
        3: "three",
        4: "four",
        5: "five",
        6: "six",
    }
    column = column_mapping.get(attempts)

    distribution = get_distribution(user_id)

    distribution[column] += 1

    sql = text("SELECT 1 FROM distributions WHERE user_id = :user_id")
    result = db.session.execute(sql, {"user_id": user_id}).fetchone()

    sql = text("""
        INSERT INTO distributions (user_id, one, two, three, four, five, six)
        VALUES (:user_id, :one, :two, :three, :four, :five, :six)
    """)
    
    if result:
        sql = text(f"""
            UPDATE distributions
            SET one = :one, two = :two, three = :three, four = :four, five = :five, six = :six
            WHERE user_id = :user_id
        """)

    db.session.execute(sql, {
        "user_id": user_id,
        "one": distribution["one"],
        "two": distribution["two"],
        "three": distribution["three"],
        "four": distribution["four"],
        "five": distribution["five"],
        "six": distribution["six"],
    })
    db.session.commit()

def get_distribution(user_id):
    sql = text("""
        SELECT one, two, three, four, five, six
        FROM distributions
        WHERE user_id = :user_id
    """)
    result = db.session.execute(sql, {"user_id": user_id}).fetchone()

    return {
        "one": result[0],
        "two": result[1],
        "three": result[2],
        "four": result[3],
        "five": result[4],
        "six": result[5],
    }