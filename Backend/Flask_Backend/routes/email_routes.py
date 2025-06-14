from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import db
from service.email_service import EmailService
from service.stats_service import EmailStatsService
from utils.logs import get_logger

email_bp = Blueprint("emails", __name__, url_prefix="/emails")

email_service = EmailService(db.session)
stats_service = EmailStatsService(db.session)
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

@email_bp.route('/predict/email', methods=['POST'])
def predict_email_from_extension():
    data = request.get_json()
    subject = data.get('subject', '')
    sender = data.get('sender', '')
    body = data.get('body', '')

    result = email_service.predict_from_extension(subject, sender, body)

    logger.info("VirusTotal prediction: {}".format(result["vt_prediction"]))

    return jsonify({
        "text_prediction": result["text_prediction"],
        "url_prediction": result["url_prediction"],
        "vt_prediction": result["vt_prediction"],
        "verdict": result["verdict"]
    })


@email_bp.route("/report-fp", methods=["POST"])
def report_false_positive():
    data = request.get_json()
    logger.info("[USER REPORT] False Positive reported: {}".format(data))
    return jsonify({"status": "ok"}), 200

@email_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_email_stats():
    user_id = get_jwt_identity()
    return stats_service.get_summary_for_user(user_id)
