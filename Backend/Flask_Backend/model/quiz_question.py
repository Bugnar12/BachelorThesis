from database import db


class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)

    def __init__(self, question, option_a, option_b, option_c, option_d, correct_answer, difficulty):
        self.question = question
        self.option_a = option_a
        self.option_b = option_b
        self.option_c = option_c
        self.option_d = option_d
        self.correct_answer = correct_answer
        self.difficulty = difficulty

    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'options': {
                'option_a': self.option_a,
                'option_b': self.option_b,
                'option_c': self.option_c,
                'option_d': self.option_d
            },
            'correct_answer': self.correct_answer,
            'difficulty': self.difficulty
        }

    def from_dict(self, data):
        for field in ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'difficulty']:
            if field in data:
                setattr(self, field, data[field])

