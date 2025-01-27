from flask import Flask
from flask_login import LoginManager
from routes import app_routes
from db import db
import os

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv("SECRET_KEY")

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'app_routes.signin'


@login_manager.user_loader
def load_user(user_id):
    from models.users import User
    return User.get_user_by_id(user_id)

app.register_blueprint(app_routes)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
