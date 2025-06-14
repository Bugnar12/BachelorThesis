import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from model.quiz_question import QuizQuestion
from repository.repository import Repository

# This script was used purely for seeding the quiz questions in DB

with app.app_context():
    repo = Repository(db.session)

    q1 = QuizQuestion(
        question="What is a common sign of a phishing email?",
        option_a="An official company logo",
        option_b="Generic greeting like 'Dear Customer'",
        option_c="Correct grammar throughout",
        option_d="Personalized name and photo",
        correct_answer='B',
        difficulty='easy',
    )

    q2 = QuizQuestion(
        question="Which URL is most likely a phishing attempt?",
        option_a="https://paypal.com/account",
        option_b="https://accounts.google.com/login",
        option_c="http://secure.paypa1.com/login",
        option_d="https://github.com/login",
        correct_answer='C',
        difficulty='medium',
    )

    q3 = QuizQuestion(
        question="Spear phishing is best described as:",
        option_a="Mass mailing to thousands of users",
        option_b="Targeting a specific individual or organization",
        option_c="Phishing via social media only",
        option_d="Using software to scan networks",
        correct_answer='B',
        difficulty='medium',
    )

    repo.add_quiz_question(q1)
    repo.add_quiz_question(q2)
    repo.add_quiz_question(q3)
