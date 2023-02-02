from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"

#creates app and database, registers auth blueprint
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'pulsic rahhhhhh'
    app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .auth import auth
    app.register_blueprint(auth, url_prefix='/')
    
    from .models import User

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
   

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    with app.app_context():
        db.create_all()
    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)