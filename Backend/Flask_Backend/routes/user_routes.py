import json

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
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


@user_bp.route("/push/subscribe", methods=["POST", "OPTIONS"])
@jwt_required(optional=True)
def subscribe_push():
    # Return early for OPTIONS requests (used in CORS preflight)
    if request.method == 'OPTIONS':
        return jsonify({'message': 'OK'}), 200

    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Missing or invalid token"}), 401

    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    subscription = request.get_json()
    user.push_subscription = json.dumps(subscription)
    db.session.commit()

    return jsonify({"message": "Subscription saved"}), 200
