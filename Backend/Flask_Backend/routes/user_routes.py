import json

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from model.user import User
from database import db
from service.user_service import UserService

user_bp = Blueprint("user", __name__, url_prefix="/users")
user_service = UserService(db.session)

@user_bp.route("/", methods=["GET"])
def get_all_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@jwt_required()
@user_bp.route("/push/subscribe", methods=["POST", "OPTIONS"])
def subscribe_push():
    user_id = get_jwt_identity()
    user = db.session.query(User).filter_by(id=user_id).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    subscription = request.get_json()
    user.push_subscription = json.dumps(subscription)
    db.session.commit()

    return jsonify({"message": "Subscription saved"}), 200
