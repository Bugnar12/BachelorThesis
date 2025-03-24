from flask import Blueprint, request

email_bp = Blueprint("emails", __name__, url_prefix="/emails")


@email_bp.route("/upload", methods=["POST"])
def upload_email():
    file = request.files["file"]
    file_path = "uploads/{}".format(file.filename)
    file.save(file_path)

    email = "empty"

    return email.to_dict(), 201

@email_bp.route("/predict", methods=["POST"])
def predict_email():
    pass