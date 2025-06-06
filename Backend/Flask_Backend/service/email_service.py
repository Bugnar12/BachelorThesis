from urllib.parse import urlparse

from repository.repository import Repository
from service.classifier_service import ClassifierService
from service.virustotal_service import VirusTotalService
from utils.email_utils import load_model, extract_domain, preprocess_text, resolve_redirect_url
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
        processed_email_body = preprocess_text(email_body)
        logger.info(self.__model.classes_)
        probabilities = self.__model.predict_proba([processed_email_body])[0]
        prediction = "Phishing text" if probabilities[0] >= 0.7 else "Safe text"
        email.text_prediction = prediction
        logger.info("prediction is {} and proba is {}".format(prediction, probabilities[1]))

        return {"prediction": prediction }

    def predict_email_text_direct(self, body: str):
        processed_text = preprocess_text(body)
        if not processed_text.strip():
            return {"prediction": "text is empty after preprocessing"}
        probabilities = self.__model.predict_proba([processed_text])[0]
        prediction = "Phishing text" if probabilities[0] >= 0.8 else "Safe text"
        return {"prediction": prediction}


    def predict_url_virustotal(self, url):
        domain = url
        logger.info("Domain in virusTotal: {}".format(domain))
        vt_dns_info = self.__vt_service.get_vt_dns_info(domain)
        vt_report = self.__vt_service.get_vt_dns_report_results(vt_dns_info)

        return {
            "prediction": vt_report["final_verdict"],
            # TODO: the below fields will be added in an extended report
            # "summary": vt_report["summary"],
            # "triggers": vt_report["triggers"]
        }

    def get_paginated_emails_for_user(self, user_id, page, page_size):
        query = self.__repository.get_emails_query_by_user(user_id)
        paginated = query.paginate(page=page, per_page=page_size, error_out=False)
        return {
            "items": paginated.items,
            "total": paginated.total
        }

    def predict_url(self, url):
        return self.__classifier.classify_url(url)

    def get_emails_for_user(self, user_id):
        return self.__repository.get_emails_by_user(user_id)

    def predict_from_extension(self, subject: str, sender: str, body: str) -> dict:
        logger.info("[EXTENSION] Analyzing email from {} with subject '{}'".format(sender, subject))

        text_result = self.predict_email_text_direct(body)
        text_pred = text_result["prediction"]

        urls = email_utils.extract_urls_from_body(body)
        urls = email_utils.postprocess_urls(urls)
        logger.info("Postprocessed URLs: {}".format(urls))

        url_pred = "No URL found"
        vt_pred = "No URL found"
        phishing_url_detected = False
        vt_phishing_detected = False

        for url in urls:
            parsed = urlparse(url)
            minimal_url = "{}://{}".format(parsed.scheme, parsed.netloc)

            logger.info("[EXTENSION] Stripped URL: {} → {}".format(url, minimal_url))

            # AI-based URL prediction
            url_result = self.predict_url(minimal_url)
            url_label = url_result.get("label", "unknown")
            logger.info("[EXTENSION] URL AI Prediction: {} → {}".format(minimal_url, url_label))

            vt_result = self.predict_url_virustotal(minimal_url)
            vt_label = vt_result.get("prediction", "unknown")
            if isinstance(vt_label, list):
                vt_label = vt_label[0]

            logger.info("[EXTENSION] VirusTotal Prediction: {} → {}".format(minimal_url, vt_label))

            if url_label.lower() == "phishing":
                phishing_url_detected = True
                url_pred = "phishing"

            elif url_pred == "No URL found":
                url_pred = url_label

            if vt_label.lower() == "phishing":
                vt_phishing_detected = True
                vt_pred = "phishing"

            elif vt_pred == "No URL found":
                vt_pred = vt_label

        # Final verdict
        if "phishing" in text_pred.lower() or phishing_url_detected or vt_phishing_detected:
            verdict = "phishing"
        else:
            verdict = "legitimate"

        logger.info("vt_prediction: {}".format(vt_pred))

        return {
            "text_prediction": text_pred,
            "url_prediction": url_pred,
            "vt_prediction": vt_pred,
            "verdict": verdict
        }