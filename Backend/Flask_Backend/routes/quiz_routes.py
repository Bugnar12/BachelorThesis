from flask import Blueprint, jsonify, abort, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from database import db
from model.quiz_attempt import QuizAttempt
from model.quiz_question import QuizQuestion
from model.user_quiz_answers import UserQuizAnswer
from service.quiz_service import QuizService

quiz_bp = Blueprint("quiz", __name__, url_prefix="/quiz")
quiz_service = QuizService(db.session)

@quiz_bp.route('/questions', methods=['GET'])
@jwt_required()
def get_all_questions():
    return quiz_service.get_random_questions()


@quiz_bp.route('/questions/<int:question_id>', methods=['GET'])
def get_question_by_id(question_id):
    return quiz_service.get_question_by_id(question_id)


@quiz_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_quiz():
    user_id = get_jwt_identity()
    return quiz_service.submit_quiz(user_id, request.json)


@quiz_bp.route('/history', methods=['GET'])
@jwt_required()
def get_quiz_history():
    user_id = get_jwt_identity()
    return quiz_service.get_history(user_id)

