from flask import Blueprint, jsonify

from model.user import User

user_bp = Blueprint("user", __name__, url_prefix="/users")

@user_bp.route("/", method="GET")
def get_all_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route("/", method="POST")
def create_user():
    pass

user_bp.route("/<int:user_id>", method="GET")
def get_user():
    pass
