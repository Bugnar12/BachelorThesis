import json
from flask import jsonify

from repository.repository import Repository
from model.email import Email
from utils.logs import get_logger

logger = get_logger()


class EmailStatsService:
    def __init__(self, db_session):
        self.__repository = Repository(db_session)

    def get_summary_for_user(self, user_id: int):
        query = self.__repository.get_emails_query_by_user(user_id)

        total = query.count()
        phishing = query.filter(Email.final_verdict == 'phishing').count()
        legitimate = query.filter(Email.final_verdict == 'legitimate').count()

        detection_counts = {
            'ai_url': 0,
            'ai_text': 0,
            'vt': 0,
            'uncategorized': 0
        }

        for email in query.all():
            detection_counts[self.detect_source(email)] += 1

        # ⬇️ 30-minute slots, last 24 h (adjust days as needed)
        timeline_rows = self.__repository.get_email_timeline_by_user(
            user_id, days=1, slot_minutes=30
        )

        timeline = [
            {
                "date": row.slot.isoformat(timespec="seconds"),
                "count": int(row.count),
                "phishing": int(row.phishing)
            }
            for row in timeline_rows
        ]

        payload = {
            "total": total,
            "phishing": phishing,
            "legitimate": legitimate,
            "detection_breakdown": detection_counts,
            "timeline": timeline
        }

        logger.info(payload)
        return jsonify(payload)

    def detect_source(self, email):
        try:
            vt = json.loads(email.vt_domain_result or '{}')
            url_ai = json.loads(email.url_prediction or '{}')
            text_ai = json.loads(email.text_prediction or '{}')

            if vt.get('label') == 'phishing':
                return 'vt'
            if url_ai.get('label') == 'phishing':
                return 'ai_url'
            if text_ai.get('prediction') == 'Phishing text':
                return 'ai_text'
        except Exception:
            pass

        return 'uncategorized'
