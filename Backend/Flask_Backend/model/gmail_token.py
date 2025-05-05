from google.oauth2.credentials import Credentials

from database import db

class GmailToken(db.Model):
    __tablename__ = "gmail_tokens"

    gmail_token_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    id_token = db.Column(db.Text, nullable=True)
    token_uri = db.Column(db.Text, nullable=False)
    client_id = db.Column(db.Text, nullable=False)
    client_secret = db.Column(db.Text, nullable=False)
    scopes = db.Column(db.Text, nullable=False)

    @classmethod
    def from_credentials(cls, user_id, creds: Credentials):
        return cls(
            user_id=user_id,
            access_token=creds.token,
            refresh_token=creds.refresh_token,
            token_uri=creds.token_uri,
            client_id=creds.client_id,
            client_secret=creds.client_secret,
            scopes=','.join(creds.scopes),
        )