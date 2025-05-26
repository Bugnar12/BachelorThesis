# CONSTANTS SECTION
DOMAIN_URL_MXTOOL = r'https://api.mxtoolbox.com/api/v1/Lookup/Blacklist/{}?Authorization={}'
# TODO: replace with more relative path
AI_MODEL_ABS_PATH = r'c:\Users\Edy\phishing_better_preprocessing.pkl'
POLLING_INTERVAL = 30
HF_API_URL = r'https://api-inference.huggingface.co/models/CrabInHoney/urlbert-tiny-v4-phishing-classifier'
HF_MODEL_NAME = r'CrabInHoney/urlbert-tiny-v4-phishing-classifier'
VT_BASE_URL = r'https://www.virustotal.com/api/v3'
# TODO: implement the shortening url feature + mention in documentation
URL_SHORTENERS = [
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "buff.ly",
    "rebrand.ly", "is.gd", "shorte.st", "bl.ink", "cut.ly", "cutt.ly"
]
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')