import json

from flask import Blueprint, jsonify, request, render_template, session
from models import User, Game, GameUser, GameCards, user_to_dto, game_to_dto
from app import db
from flask_login import login_user, logout_user, current_user, login_required

api = Blueprint('api', __name__)


@api.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.json['username']
    if current_user.is_authenticated:
        user = User.query.get(current_user.id)
        if user:
            if username != "":
                user.username = username
            else:
                user.username = "Unknown"
            db.session.commit()
            return jsonify(user_to_dto(user))
    if username != "":
        user = User(username=username)
    else:
        user = User()
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return jsonify(user_to_dto(user))


@api.route('/current', methods=['GET'])
def get_user():
    if current_user.is_authenticated:
        return jsonify(user_to_dto(current_user))
    return jsonify("NotAuthenticated")


@api.route('/logout')
def logout():
    # if current_user.is_authenticated:
    #     user = User.query.get(current_user.id)
    #     if user:
    #         db.session.delete(user)
    #         db.session.commit()
    logout_user()
    return jsonify("LoggedOut")


@api.route('/create')
@login_required
def create():
    game = Game(admin_id=current_user.id)
    db.session.add(game)
    db.session.commit()
    game_user = GameUser(user_id=current_user.id, game_id=game.id)
    db.session.add(game_user)
    db.session.commit()
    session['game_id'] = game.id
    session.permanent = False
    session.modified = True
    return jsonify(game_to_dto(game))


@api.route('/game')
def get_game():
    if 'game_id' in session.keys():
        if current_user.is_authenticated:
            game = Game.query.get(session['game_id'])
            if game:
                return jsonify(game_to_dto(game))
        session.pop('game_id')
    return jsonify("GameNotFound")


@api.route('/start')
@login_required
def start_game():
    if 'game_id' in session.keys():
        game = Game.query.get(session['game_id'])
        if game and game.admin_id == current_user.id:
            game.is_started = True
            db.session.commit()
            return jsonify(game_to_dto(game))
        return jsonify("NoPermission")
    return jsonify("GameNotFound")



@api.route('/cancel')
def cancel_game():
    if 'game_id' in session.keys():
        game_user = GameUser.query.filter_by(user_id=current_user.id, game_id=session['game_id']).first()
        if game_user is not None:
            db.session.delete(game_user)
            db.session.commit()
        session.pop('game_id')
    return jsonify("GameCanceled")


@api.route('/join', methods=["POST"])
@login_required
def join_game():
    game_id = request.json['id']
    game = Game.query.get(game_id)
    if game:
        session['game_id'] = game_id
        session.permanent = False
        session.modified = True
        if GameUser.query.filter_by(user_id=current_user.id, game_id=game_id).first() is None:
            game_user = GameUser(user_id=current_user.id, game_id=game_id)
            db.session.add(game_user)
            db.session.commit()
            return jsonify(game_to_dto(game))
    return jsonify("GameNotFound")


@api.route('/members')
@login_required
def get_members():
    if 'game_id' in session.keys():
        members = GameUser.query.filter_by(game_id=session['game_id']).all()
        members_names = []
        for member in members:
            user = User.query.get(member.user_id);
            members_names.append(user.username)
        return json.dumps(members_names)
    return jsonify("GameNotFound")


@api.route('/cards')
@login_required
def get_cards():
    if 'game_id' in session.keys():
        cards = GameCards.query.filter_by(game_id=session['game_id']).all()
        cards_list = []
        for card in cards:
            cards_list.append({
                "id": card.card_id,
                "sprint": card.sprint_id,
                "is_grabbed": card.is_grabbed,
                "user_id": card.user_id
            })
        return json.dumps(cards_list)
    return jsonify("GameNotFound")


@api.route('/grabbed', methods=['POST'])
@login_required
def card_grabbed():
    print(request.json)
    if 'game_id' in session.keys():
        card_id = request.json['id']
        card = GameCards.query.filter_by(game_id=session['game_id'], card_id=card_id).first()
        if card:
            card.is_grabbed = True
            card.user_id = current_user.id
        else:
            card = GameCards(game_id=session['game_id'], card_id=card_id, is_grabbed=True, user_id=current_user.id)
            db.session.add(card)
        db.session.commit()
        return jsonify("Done")
    return jsonify('GameNotFound')


@api.route('/dropped', methods=['POST'])
@login_required
def card_dropped():
    print(request.json)
    if 'game_id' in session.keys():
        card_id = request.json['id']
        sprint_id = request.json['sprint_id']

        card = GameCards.query.filter_by(game_id=session['game_id'], card_id=card_id).first()
        if card:
            card.is_grabbed = False
            card.sprint_id = sprint_id
            card.user_id = None
        else:
            card = GameCards(game_id=session['game_id'], card_id=card_id, sprint_id=sprint_id)
            db.session.add(card)
        db.session.commit()
        return jsonify("Done")

    return jsonify('GameNotFound')


@api.route("/")
def my_index():
    return render_template("index.html")
