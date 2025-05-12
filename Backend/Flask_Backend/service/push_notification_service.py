import json
from pywebpush import webpush, WebPushException
from config.config import VAPIDConfig
from utils.logs import get_logger

logger = get_logger()


class PushNotificationService:
    def __init__(self, db_session):
        self.db_session = db_session

    def send_notification(self, subscription_info, title, body, url="http://localhost:4200/manual-analyze"):
        try:
            payload = json.dumps({
                "title": title,
                "body": body,
                "url": url
            })

            webpush(
                subscription_info=subscription_info,
                data=payload,
                vapid_private_key=VAPIDConfig.VAPID_PRIVATE_KEY,
                vapid_claims=VAPIDConfig.VAPID_CLAIMS
            )

            logger.info("Push notification sent successfully.")
        except WebPushException as ex:
            logger.error("Push notification failed: {}".format(ex))

    def notify_user_phishing_email(self, user, email_subject, email_sender):
        if not user.push_subscription:
            logger.warning("User {} does not have a push subscription.".format(user.user_email))
            return

        self.send_notification(
            subscription_info=json.loads(user.push_subscription),
            title="!!! Suspicious Email Detected !!!",
            body="From {}: {}".format(email_sender, email_subject),
            url="http://localhost:4200/manual-analyze"
        )