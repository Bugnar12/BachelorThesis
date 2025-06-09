import time
from datetime import datetime

import requests

from config.config import Config
from utils import definitions
from utils.logs import get_logger

logger = get_logger()


class VirusTotalService:
    def __init__(self):
        self.__vt_api_key = Config.VT_API_KEY
        self.__base_url = definitions.VT_BASE_URL

    def get_vt_dns_info(self, domain):
        if isinstance(domain, list):
            domain = domain[0]
        domain = domain.replace("https://", "").replace("http://", "").strip("/")
        vt_url_endpoint = "{}/domains/{}".format(self.__base_url, domain)
        headers = {
            "x-apikey": self.__vt_api_key
        }
        response = requests.get(vt_url_endpoint, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error("yError fetching data from VT API: {}".format(response.status_code))
            return None

    def get_vt_dns_report_results(self, vt_data):
        if vt_data is None:
            logger.warning("VirusTotal data is None, cannot extract DNS report.")
            return {
                "final_verdict": "unknown"
            }
        attr = vt_data.get("data", {}).get("attributes", {})

        reputation = attr.get("reputation", 0)
        creation_date = attr.get("creation_date")
        # domain_age = self.__compute_domain_age(creation_date)
        domain_age = 40 # TODO: fix the domain_age

        last_analysis_stats = attr.get("last_analysis_stats", {})
        malicious = last_analysis_stats.get("malicious", 0)
        suspicious = last_analysis_stats.get("suspicious", 0)
        harmless = last_analysis_stats.get("harmless", 0)

        triggers = self.__generate_trigger_report(malicious, suspicious, reputation, domain_age)
        domain_safe_verdict = self.__decide_verdict(malicious, suspicious, reputation, domain_age)

        return {
            "final_verdict": domain_safe_verdict,
            "summary": {
                "malicious": malicious,
                "suspicious": suspicious,
                "harmless": harmless,
                "reputation": reputation,
                "domain_age": creation_date,
            },
            "triggers": triggers
        }

    def check_file_hash(self, file_path):
        vt_file_hash_endpoint = "{}/files".format(self.__base_url, file_path)
        headers = {
            "x-apikey": self.__vt_api_key
        }
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f)}
            response = requests.post(vt_file_hash_endpoint, headers=headers, files=files)
        return response.json()

    def get_analysis_report(self, analysis_id):
        url = "{}/analyses/{}".format(self.__base_url, analysis_id)
        headers = {
            "x-apikey": self.__vt_api_key
        }

        while True:
            response = requests.get(url, headers=headers)
            data = response.json()

            status = data.get("data", {}).get("attributes", {}).get("status")
            if status == "completed":
                return data
            else:
                print("Waiting for analysis to complete...")
                time.sleep(3)  # Wait before polling again

    @staticmethod
    def __compute_domain_age(creation_ts):
        if not creation_ts:
            return None
        try:
            return int((datetime.utcnow() - datetime.utcfromtimestamp(creation_ts)).days)
        except Exception as e:
            logger.warning("Invalid creation timestamp: {} – {}".format(creation_ts, e))
            return None

    @staticmethod
    def __generate_trigger_report(malicious_score, suspicious_score, reputation_score, domain_age_days):
        triggers = []

        if malicious_score > 0:
            triggers.append("{} engines flagged the domain as malicious".format(malicious_score))
        if suspicious_score > 0:
            triggers.append("{} engines flagged the domain as suspicious".format(suspicious_score))
        if reputation_score < 0:
            triggers.append("Domain reputation is low: [{}]".format(reputation_score))
        if domain_age_days is not None and domain_age_days < 30:
            triggers.append("Domain is newly registered ({} days old)".format(domain_age_days))

        return triggers

    @staticmethod
    def __decide_verdict(malicious_score, suspicious_score, reputation_score, domain_age_days):
        verdict = []

        if malicious_score > 0:
            verdict.append("potentially phishing")
        if suspicious_score > 0:
            verdict.append("suspicious")
        if reputation_score < 0:
            verdict.append("low reputation")
        if domain_age_days < 30:
            verdict.append("new domain")

        if not verdict:
            verdict.append("safe")

        return verdict
