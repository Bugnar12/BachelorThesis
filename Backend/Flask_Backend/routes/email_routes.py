from flask import Blueprint, request, jsonify

from database import db
from service.email_service import EmailService
from utils.logs import get_logger

email_bp = Blueprint("emails", __name__, url_prefix="/emails")

email_service = EmailService(db.session)
logger = get_logger()

@email_bp.route("/upload", methods=["POST"])
def upload_email():
    file = request.files["file"]
    file_path = "uploads/{}".format(file.filename)
    file.save(file_path)

    email = "empty"

    return email.to_dict(), 201

@email_bp.route("/predict_email", methods=["POST"])
def predict_email():
    data = request.get_json()
    email_id = data.get("email_id")

    result = email_service.predict_email_text(email_id)
    return jsonify({'email_id': email_id, 'result': result}), 200