import email
from email import policy
from utils.logs import get_logger

email_path = "email.eml"
logger = get_logger()

def parse_email_information(email_path):
    with open(email_path, "r", encoding="utf-8") as email_file:
        email_content = email.message_from_file(email_file, policy=policy.default)

    return email_content

def get_email_header(email_content):
    header = dict(email_content.items())
    return header


def get_email_body(email_content):
    """Extracts the plain text body from the email content."""
    body = None
    if email_content.is_multipart():
        for part in email_content.walk():
            if part.get_content_type() == "text/plain":  # Extract plain text body
                body = part.get_payload(decode=True).decode(part.get_content_charset(), errors="ignore")
                break  # Stop after getting the first plain text part
    else:
        body = email_content.get_payload(decode=True).decode(email_content.get_content_charset(), errors="ignore")

    return body

# def get_domain(content):
#     from_header = content["From"]
#     # regexp section
#     domain_match = re.search(r'@([\w.-]+)', from_header)
#     print(domain_match.group(0).strip('@'))

if __name__ == "__main__":
    parsed_content = parse_email_information(email_path)
    test_email_header = get_email_header(parsed_content)
    test_email_body = get_email_body(parsed_content)
    logger.info("Header: {}".format(test_email_header))
    logger.info("Body: {}".format(test_email_body))
    logger.info("Multipart: {}".format(parsed_content.is_multipart()))