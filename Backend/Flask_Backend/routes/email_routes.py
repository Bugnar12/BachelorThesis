from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import db
from service.email_service import EmailService
from utils.logs import get_logger

email_bp = Blueprint("emails", __name__, url_prefix="/emails")

email_service = EmailService(db.session)
logger = get_logger()

@email_bp.route("/predict_email", methods=["POST"])
def predict_email():
    data = request.get_json()
    email_id = data.get("email_id")
    result = email_service.predict_email_text(email_id)

    return jsonify({
        'email_id': email_id,
        'result': result
    }), 200

@email_bp.route("/get_emails", methods=["GET"])
@jwt_required()
def get_emails():
    user_id = get_jwt_identity()
    emails = email_service.get_emails_for_user(user_id)
    # converting to list of dicts to send JSON response
    dict_emails = [email.to_dict() for email in emails]
    return jsonify(dict_emails), 200