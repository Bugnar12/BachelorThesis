from flask import Blueprint, jsonify, request

from model.user import User
from database import db
from service.user_service import UserService

user_bp = Blueprint("user", __name__, url_prefix="/users")
user_service = UserService(db.session)

@user_bp.route("/", methods=["GET"])
def get_all_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()

    user = user_service.register_user(data)
    return user.to_dict(), 201

@user_bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()

    user = user_service.login_user(data)
    return user.to_dict(), 201
