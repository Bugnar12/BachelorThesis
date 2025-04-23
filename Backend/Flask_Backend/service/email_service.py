from model.email import Email
from repository.repository import Repository
from service.classifier_service import ClassifierService
from utils.email_utils import get_email_header, load_model, get_email_body
from utils.logs import get_logger

logger = get_logger()

class EmailService:
    def __init__(self, db_session):
        self.__repository = Repository(db_session)
        self.__model = load_model()
        self.__classifier = ClassifierService()

    def predict_email_text(self, email_id):
        email = Email.query.filter_by(email_id=email_id).first() # TODO: add this in the repository instead
        email_body = email.email_body
        probabilities = self.__model.predict_proba([email_body])[0]

        prediction = "Potentially phishing email" if probabilities[1] >= 0.7 else "Safe email"

        return {
            "prediction": prediction  # e.g., 'phishing' or 'safe'
        }

    def predict_url(self, url):
        return self.__classifier.classify_url(url)

    def get_emails_for_user(self, user_id):
        return self.__repository.get_emails_by_user(user_id)