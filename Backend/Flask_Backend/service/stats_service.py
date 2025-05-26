import json
from datetime import datetime, timedelta
from flask import jsonify
from sqlalchemy import func

from repository.repository import Repository
from model.email import Email


class EmailStatsService:
    def __init__(self, db_session):
        self.__repository = Repository(db_session)

    def get_summary_for_user(self, user_id):
        query = self.__repository.get_emails_query_by_user(user_id)

        total = query.count()
        phishing = query.filter(Email.final_verdict == 'phishing').count()
        legitimate = query.filter(Email.final_verdict == 'legitimate').count()

        emails = query.all()
        detection_counts = {
            'ai_url': 0,
            'ai_text': 0,
            'vt': 0,
            'uncategorized': 0
        }

        for email in emails:
            detected_by = self.detect_source(email)
            detection_counts[detected_by] += 1

        last_30_days = datetime.utcnow() - timedelta(days=30)
        timeline_data = self.__repository.session.query(
            func.date(Email.email_timestamp), func.count()
        ).filter(
            Email.user_id == user_id,
            Email.email_timestamp >= last_30_days
        ).group_by(func.date(Email.email_timestamp)).all()

        return jsonify({
            'total': total,
            'phishing': phishing,
            'legitimate': legitimate,
            'detection_breakdown': detection_counts,
            'timeline': [{'date': str(d), 'count': c} for d, c in timeline_data]
        })

    def detect_source(self, email):
        try:
            vt = json.loads(email.vt_domain_result or '{}')
            url_ai = json.loads(email.url_prediction or '{}')
            text_ai = json.loads(email.text_prediction or '{}')

            if vt.get('label') == 'phishing':
                return 'vt'
            if url_ai.get('label') == 'phishing':
                return 'ai_url'
            if text_ai.get('label') == 'phishing':
                return 'ai_text'
        except Exception:
            pass

        return 'uncategorized'
