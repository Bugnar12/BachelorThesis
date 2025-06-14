import json
import os

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pywebpush import webpush, WebPushException

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

    user = db.session.query(User).filter_by(user_id=user_id).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    subscription = request.get_json()
    user.push_subscription = json.dumps(subscription)
    db.session.commit()

    return jsonify({"message": "Subscription saved"}), 200

@user_bp.route('/push/send', methods=['POST'])
@jwt_required()
def send_push():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.push_subscription:
        return jsonify({"error": "User not subscribed"}), 400

    payload = request.get_json().get("message", "You have a new notification!")
    subscription_info = json.loads(user.push_subscription)

    try:
        webpush(
            subscription_info,
            data=json.dumps({"title": "Phishing Alert", "body": payload}),
            vapid_private_key=os.getenv("VAPID_PRIVATE_KEY"),
            vapid_claims={"sub": os.getenv("VAPID_EMAIL")}
        )
        return jsonify({"message": "Notification sent!"}), 200
    except WebPushException as ex:
        print("Web push failed:", repr(ex))
        return jsonify({"error": "Push failed"}), 500
