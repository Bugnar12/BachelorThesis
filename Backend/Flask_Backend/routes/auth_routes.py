from datetime import timedelta

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_access_token():
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=str(user_id), expires_delta=timedelta(minutes=15))
    return jsonify(access_token=new_access_token), 200