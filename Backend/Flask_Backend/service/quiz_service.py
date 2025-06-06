from flask import jsonify, abort
from model.quiz_attempt import QuizAttempt
from model.user_quiz_answers import UserQuizAnswer
from database import db
from repository.repository import Repository


class QuizService:
    def __init__(self, db_session):
        self.repo = Repository(db_session)

    def get_random_questions(self):
        questions = self.repo.fetch_random_questions(limit=10)
        return jsonify([q.to_dict() for q in questions]), 200

    def get_question_by_id(self, question_id):
        question = self.repo.fetch_question_by_id(question_id)
        if not question:
            abort(404, description="Question with ID {} not found.".format(question_id))
        return jsonify(question.to_dict()), 200

    def submit_quiz(self, user_id, data):
        answers_data = data['answers']
        score = 0
        total = len(answers_data)

        attempt = QuizAttempt(user_id=user_id, score=0, total_questions=total)
        db.session.add(attempt)
        db.session.flush()

        for entry in answers_data:
            q = self.repo.fetch_question_by_id(entry['question_id'])

            selected_opt = entry['selected_option']
            if not hasattr(q, selected_opt):
                return jsonify({"error": "Invalid selected option: {}".format(selected_opt)}), 400

            correct_value = getattr(q, q.correct_answer)
            selected_value = getattr(q, selected_opt)
            is_correct = selected_value == correct_value
            if is_correct:
                score += 1

            db.session.add(UserQuizAnswer(
                user_id=user_id,
                question_id=q.id,
                selected_option=selected_opt,
                is_correct=is_correct,
                attempt_id=attempt.id
            ))

        attempt.score = score
        db.session.commit()
        return jsonify({'message': 'Quiz submitted', 'score': score, 'total': total})

    def get_history(self, user_id):
        attempts = self.repo.fetch_user_attempts(user_id)
        result = []

        for idx, attempt in enumerate(reversed(attempts), start=1):
            answers = self.repo.fetch_answers_for_attempt(attempt.id)
            question_ids = [a.question_id for a in answers]
            question_map = {q.id: q for q in self.repo.fetch_questions_by_ids(question_ids)}

            questions_detail = []
            for answer in answers:
                question = question_map.get(answer.question_id)
                if not question:
                    continue
                correct_answer_text = getattr(question, question.correct_answer)
                user_answer_text = getattr(question, answer.selected_option)
                questions_detail.append({
                    "text": question.question,
                    "userAnswer": user_answer_text,
                    "correctAnswer": correct_answer_text
                })

            result.append({
                "attempt_no": idx,
                "timestamp": attempt.timestamp.isoformat(),
                "score": attempt.score,
                "total": attempt.total_questions,
                "questions": questions_detail
            })

        return jsonify(result)
