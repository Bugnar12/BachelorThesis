from datetime import datetime

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

    email_timestamp = db.Column(db.DateTime, default=datetime.now())
    user = db.relationship("User", backref="processed_emails")

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
            "email_sender": self.email_sender,
            "email_recipient": self.email_recipient,
            "email_body": self.email_body,
        }

    def from_dict(self, data):
        for field in ["user_id", "email_sender", "email_recipient", "email_body", "email_raw_header"]:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return (
            f"Email(from='{self.email_sender}', to='{self.email_recipient}', "
            f"subject='{self.email_subject}', body='{self.email_body[:50]}...')"
        )