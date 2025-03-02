from database import db

class Email(db.Model):
    __tablename__ = "emails"

    email_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    email_sender = db.Column(db.String(255), nullable=False)
    email_recipient = db.Column(db.String(255), nullable=False)
    email_body = db.Column(db.Text, nullable=False)
    email_raw_header = db.Column(db.Text, nullable=False)

    def __init__(self, user_id, email_sender, email_recipient, email_body, email_raw_header):
        self.user_id = user_id
        self.email_sender = email_sender
        self.email_recipient = email_recipient
        self.email_body = email_body
        self.email_raw_header = email_raw_header

    def to_dict(self):
        return {
            "email_id": self.email_id,
            "user_id": self.user_id,
            "email_sender": self.email_sender,
            "email_recipient": self.email_recipient,
            "email_body": self.email_body,
            "email_raw_header": self.email_raw_header
        }

    def from_dict(self, data):
        for field in ["user_id", "email_sender", "email_recipient", "email_body", "email_raw_header"]:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return "Email: {}".format(self.email_id)