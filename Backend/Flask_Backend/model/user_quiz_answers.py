from datetime import datetime, timezone

from database import db


class UserQuizAnswer(db.Model):
    __tablename__ = 'user_quiz_answers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_questions.id'))
    selected_option = db.Column(db.String(50))
    is_correct = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime(timezone=True), default=datetime.now(timezone.utc))
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'))

    def __init__(self, user_id, question_id, selected_option, is_correct, attempt_id):
        self.user_id = user_id
        self.question_id = question_id
        self.selected_option = selected_option
        self.is_correct = is_correct
        self.attempt_id = attempt_id

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'selected_option': self.selected_option,
            'is_correct': self.is_correct,
            'timestamp': self.timestamp.isoformat()
        }

    def from_dict(self, data):
        for field in ['user_id', 'question_id', 'selected_option', 'is_correct']:
            if field in data:
                setattr(self, field, data[field])
