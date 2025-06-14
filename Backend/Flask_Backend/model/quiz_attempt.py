from datetime import datetime, timezone
from sqlalchemy import DateTime, func
from database import db


class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    score = db.Column(db.Integer)
    total_questions = db.Column(db.Integer)
    timestamp = db.Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now()
    )
    answers = db.relationship('UserQuizAnswer', backref='attempt', lazy=True)
