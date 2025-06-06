from datetime import date, timedelta, datetime

from sqlalchemy import func, text, case

from model.email import Email
from model.gmail_token import GmailToken
from model.quiz_attempt import QuizAttempt
from model.quiz_question import QuizQuestion
from model.user import User
from model.user_quiz_answers import UserQuizAnswer
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

    def get_all_quiz_questions(self):
        return self.__db.query(QuizQuestion).all()

    def get_quiz_question_by_id(self, question_id):
        return self.__db.query(QuizQuestion).filter_by(id=question_id).first()

    def get_quiz_questions_by_difficulty(self, difficulty):
        return self.__db.query(QuizQuestion).filter_by(difficulty=difficulty).all()

    def add_quiz_question(self, question):
        self.__db.add(question)
        self.__db.commit()
        return question

    def delete_quiz_question(self, question_id):
        question = self.get_quiz_question_by_id(question_id)
        if question:
            self.__db.delete(question)
            self.__db.commit()
        return question

    ###### QUIZ SECTION ######

    def fetch_random_questions(self, limit=10):
        return self.__db.query(QuizQuestion).order_by(func.random()).limit(limit).all()

    def fetch_question_by_id(self, question_id):
        return self.__db.query(QuizQuestion).get(question_id)

    def fetch_user_attempts(self, user_id):
        return self.__db.query(QuizAttempt).filter_by(user_id=user_id).order_by(
            QuizAttempt.timestamp.asc()).all()

    def fetch_answers_for_attempt(self, attempt_id):
        return self.__db.query(UserQuizAnswer).filter_by(attempt_id=attempt_id).all()

    def fetch_questions_by_ids(self, question_ids):
        return self.__db.query(QuizQuestion).filter(QuizQuestion.id.in_(question_ids)).all()

    def commit(self):
        self.__db.commit()

    def get_email_timeline_by_user(
            self,
            user_id: int,
            days: int = 1,
            slot_minutes: int = 30
    ):
        """
        Return rows like:
            slot-start-iso, total_count, phishing_count
        """
        if 60 % slot_minutes:
            raise ValueError("slot_minutes must divide evenly into an hour")

        since = datetime.utcnow() - timedelta(days=days)

        # round DOWN to nearest slot: hh:00, hh:30, ...
        table = Email.__tablename__  # 'emails'

        slot = (
                func.date_trunc('hour', Email.email_timestamp) +
                text("INTERVAL '30 minutes' * floor(date_part('minute', {}.email_timestamp) / 30)".format(table))
        ).label('slot')

        return (
            self.__db.query(
                slot,
                func.count().label('count'),
                func.sum(
                    case((Email.final_verdict == 'phishing', 1), else_=0)
                ).label('phishing')
            )
            .filter(
                Email.user_id == user_id,
                Email.email_timestamp >= since
            )
            .group_by(slot)
            .order_by(slot)
            .all()
        )
