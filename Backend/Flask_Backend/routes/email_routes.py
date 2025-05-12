from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import db
from service.email_service import EmailService
from utils.logs import get_logger

email_bp = Blueprint("emails", __name__, url_prefix="/emails")

email_service = EmailService(db.session)
logger = get_logger()

@email_bp.route("/predict_text", methods=["POST"])
@jwt_required(optional=True)
def predict_text():
    data = request.get_json()
    text = data.get("text", "")
    prediction = email_service.predict_email_text_direct(text)

    return jsonify({ 'prediction': prediction }), 200

@email_bp.route("/predict_url", methods=["POST"])
@jwt_required(optional=True)
def predict_url():
    data = request.get_json()
    url = data.get("url", "")
    if not url:
        return jsonify({"error": "Missing URL"}), 400
    prediction = email_service.predict_url(url)
    return jsonify(prediction)


@email_bp.route("/get_emails", methods=["GET"])
@jwt_required()
def get_emails():
    user_id = get_jwt_identity()
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))

    query = email_service.get_paginated_emails_for_user(user_id, page, page_size)
    emails = query["items"]
    total = query["total"]
    # converting to list of dicts to send JSON response
    dict_emails = [email.to_dict() for email in emails]

    return jsonify({
        "emails": dict_emails,
        "total": total,
        "page": page,
        "page_size": page_size
    }), 200

@email_bp.route("/get_dns_info", methods=["GET"])
def get_dns_info(url):
    # return email_service.vt_dns_info(url)
    pass