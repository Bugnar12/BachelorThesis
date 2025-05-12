from model.email import Email
from model.gmail_token import GmailToken
from model.user import User
from utils.logs import get_logger

logger = get_logger()

class Repository:

    def __init__(self, database):
        self.__db = database

    ###### USER SECTION ######

    def get_all_users(self):
        return self.__db.query(User).all()

    def get_user_by_id(self, user_id):
        return self.__db.query(User).filter_by(user_id=user_id).first()

    def add_user(self, added_user):
        """
            Adds a user to the database
        """
        self.__db.add(added_user)
        self.__db.commit()
        return added_user

    ###### EMAIL SECTION ######

    def get_emails_by_user(self, user_id):
        return self.__db.query(Email).filter_by(user_id=user_id).order_by(Email.email_timestamp.desc()).all()

    def get_user_by_email(self, email):
        """
            Finds a user by its email and returns it
        """
        return self.__db.query(User).filter_by(user_email=email).first()

    def save_email(self, email):
        """
            Saves an email object in the database
        """
        self.__db.add(email)
        self.__db.commit()

        logger.info("Email saved in database")
        return email

    def is_email_processed(self, gmail_message_id):
        return self.__db.query(Email).filter_by(gmail_message_id=gmail_message_id).first() is not None

    def get_email_by_gmail_message_id(self, gmail_message_id):
        """
            Returns an email object from the database
        """
        return self.__db.query(Email).filter_by(gmail_message_id=gmail_message_id).first()

    def get_email_by_id(self, email_id):
        """
            Returns an email object from the database
        """
        return self.__db.query(Email).filter_by(email_id=email_id).first()

    def get_emails_query_by_user(self, user_id):
        """
        Returns a query object for emails of a specific user, ordered by timestamp
        """
        return self.__db.query(Email).filter_by(user_id=user_id).order_by(Email.email_timestamp.desc())

    def save_token(self, creds, user):
        """
            Saves or updates the token for a user in the database
        """
        token = GmailToken.query.filter_by(user_id=user.user_id).first()

        # If token exists, update it
        if token:
            token.access_token = creds.token
            token.refresh_token = creds.refresh_token
            token.id_token = creds.id_token
            token.token_uri = creds.token_uri
            token.client_id = creds.client_id
            token.client_secret = creds.client_secret
            token.scopes = creds.scopes
        # If token is not found, then it shall be created
        else:
            token = GmailToken.from_credentials(user.user_id, creds)

        self.__db.add(token)
        self.__db.commit()
