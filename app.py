from flask import Flask
from flask_login import LoginManager
from models import db
from routes import app_routes

app = Flask(__name__)
app.config.from_object("config.Config")

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'app_routes.signin'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

app.register_blueprint(app_routes)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)