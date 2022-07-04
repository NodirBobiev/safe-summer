from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def user_to_dto(user):
    return {'id': user.id, 'username': user.username, 'auth_date': user.auth_date}


def game_to_dto(game):
    return {'id': game.id, 'admin_id': game.admin_id, 'is_started': game.is_started}


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, default="Unknown")
    auth_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_started = db.Column(db.Boolean, default=False)


class GameUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class GameCards(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    card_id = db.Column(db.String(150))
    is_grabbed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sprint_id = db.Column(db.String(150))

