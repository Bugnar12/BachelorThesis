import json

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from model.user import User
from database import db
from utils.logs import get_logger

push_bp = Blueprint("push", __name__, url_prefix="/push")
logger = get_logger()

@push_bp.route("/subscribe", methods=["POST"])
@jwt_required()
def subscribe_push():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    subscription_info = request.get_json()
    if not subscription_info:
        return jsonify({"error": "Invalid sub info"}), 422

    user.push_subscription = json.dumps(subscription_info)
    db.session.commit()

    logger.info("Push subscription saved for user {}".format(user.user_email))

    return jsonify({"success": True}), 201
