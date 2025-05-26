from datetime import datetime, timezone

from database import db

class Email(db.Model):
    __tablename__ = "emails"

    email_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    gmail_message_id = db.Column(db.String(255), nullable=False, unique=True)

    email_subject = db.Column(db.String(500))
    email_sender = db.Column(db.String(255), nullable=False)
    email_recipient = db.Column(db.String(255), nullable=False)
    email_body = db.Column(db.Text, nullable=False)

    email_timestamp = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))
    user = db.relationship("User", backref="processed_emails")

    text_prediction = db.Column(db.String, nullable=True)
    url_prediction = db.Column(db.String, nullable=True)
    vt_domain_result = db.Column(db.String, nullable=True)
    final_verdict = db.Column(db.String, nullable=True)

    def __init__(self, user_id, gmail_message_id, email_sender, email_subject, email_recipient, email_body):
        self.user_id = user_id
        self.gmail_message_id = gmail_message_id
        self.email_subject = email_subject
        self.email_sender = email_sender
        self.email_recipient = email_recipient
        self.email_body = email_body

    def to_dict(self):
        return {
            "email_id": self.email_id,
            "user_id": self.user_id,
            "gmail_message_id": self.gmail_message_id,
            "email_subject": self.email_subject,
            "email_sender": self.email_sender,
            "email_recipient": self.email_recipient,
            "email_body": self.email_body,
            "email_timestamp": self.email_timestamp.isoformat(),
            "text_prediction": self.text_prediction,
            "url_prediction": self.url_prediction,
            "vt_domain_result": self.vt_domain_result,
            "final_verdict": self.final_verdict
        }

    def from_dict(self, data):
        for field in ["user_id", "gmail_message_id", "email_subject",
                      "email_sender", "email_recipient", "email_body",
                      "text_prediction", "url_prediction", "vt_domain_result", "final_verdict"]:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return (
            "Email(from='{}', to='{}', "
            "subject='{}', body='{}...')"
            # Truncate body to max 50 chars for readability
            .format(self.email_sender, self.email_recipient, self.email_subject, self.email_body[:50])
        )