from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# from flask_cors import CORS
# app.config['CORS_HEADERS'] = 'Content-Type'
# cors = CORS(app, resources={r"/*": {"origins": "*"}})

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "adsf2jo8qweqFs16ads4fSDfp[FW6sEJFxDSKaegs189"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    login_manager.init_app(app)

    from models import User
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)

    from api import api
    app.register_blueprint(api)

    return app
