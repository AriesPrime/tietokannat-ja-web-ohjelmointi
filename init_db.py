from db import db

def initialize_database():
    with open('schema.sql', 'r') as schema_file:
        schema_sql = schema_file.read()
    db.session.execute(schema_sql)
    db.session.commit()

if __name__ == '__main__':
    initialize_database()