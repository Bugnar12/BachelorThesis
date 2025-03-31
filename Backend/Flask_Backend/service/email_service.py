from model.email import Email
from repository.repository import Repository
from utils.email_utils import get_email_header, load_model, get_email_body
from utils.logs import get_logger

logger = get_logger()

class EmailService:
    def __init__(self, db_session):
        self.__repository = Repository(db_session)
        self.__model = load_model()

    def handle_email(self, email):
        headers = get_email_header(email)

        # Extract relevant header information
        sender = headers.get("From", "Unknown")
        recipient = headers.get("To", "Unknown")
        subject = headers.get("Subject", "Subject not found")

        email = self.__repository.save_email(email)
        return email

    def predict_email_text(self, email_id):
        email = Email.query.filter_by(email_id=email_id).first() # TODO: add this in the repository instead
        email_body = email.email_body
        probabilities = self.__model.predict_proba([email_body])[0]

        prediction = "Potentially phishing email" if probabilities[1] >= 0.7 else "Safe email"

        return {
            "prediction": prediction,  # e.g., 'phishing' or 'safe'
            # "probabilities": probabilities[0].tolist()  # e.g., [0.1, 0.9]
        }