import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from utils.definitions import HF_MODEL_NAME
from utils.logs import get_logger

logger = get_logger()


class ClassifierService:
    def __init__(self):
        self.model_name = HF_MODEL_NAME
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        self.labels = ["benign", "phishing"]

    def classify_url(self, url):
        logger.info("Starting url classification...")
        logger.info("classification url: {}".format(url))
        inputs = self.tokenizer(url, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

        top_class = torch.argmax(probs).item()
        score = probs[0][top_class].item()

        return {
            "label": self.labels[top_class],
            "score": round(score, 2)
        }

