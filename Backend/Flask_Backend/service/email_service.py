from repository.repository import Repository
from service.classifier_service import ClassifierService
from service.virustotal_service import VirusTotalService
from utils.email_utils import load_model, extract_domain
from utils.logs import get_logger
from utils import email_utils

logger = get_logger()

class EmailService:
    def __init__(self, db_session):
        self.__repository = Repository(db_session)
        self.__model = load_model()
        self.__classifier = ClassifierService()
        self.__vt_service = VirusTotalService()

    def predict_email_text(self, email_id):
        email = self.__repository.get_email_by_id(email_id)
        email_body = email.email_body
        url = email_utils.extract_url_from_body(email.email_body)
        logger.info("URL: {}".format(url))
        if email_utils.is_url_shortened(url):
            logger.info("URL is shortened")
            url = email_utils.unshorten_url(url)
            logger.info("Unshortened URL: {}".format(url))

        probabilities = self.__model.predict_proba([email_body])[0]
        prediction = "Potentially phishing email" if probabilities[1] >= 0.7 else "Safe email"
        domain_from_url = extract_domain(url[0])
        vt_dns_info = self.__vt_service.get_vt_dns_info(domain_from_url)
        vt_report = self.__vt_service.get_vt_dns_report_results(vt_dns_info)

        return {
            "prediction": prediction,  # e.g. 'phishing' or 'safe'
            "vt_prediction": vt_report,
        }

    def predict_url(self, url):
        return self.__classifier.classify_url(url)

    def get_emails_for_user(self, user_id):
        return self.__repository.get_emails_by_user(user_id)