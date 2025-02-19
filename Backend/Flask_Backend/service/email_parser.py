import email
import re


def parse_email_information():
    with open("email.eml", "r") as email_file:
        email_content = email.message_from_file(email_file)

    return email_content

def get_domain(content):
    from_header = content["From"]
    # regexp section
    domain_match = re.search(r'@([\w.-]+)', from_header)
    print(domain_match.group(0).strip('@'))

if __name__ == "__main__":
    parsed_content = parse_email_information()
    get_domain(parsed_content)