import spacy
from nlu.config import MODEL_PATH, INTENT_THRESHOLD

class MLIntentClassifier:
    def __init__(self, model_path=MODEL_PATH, threshold=INTENT_THRESHOLD):
        self.nlp = None
        self.model_path = model_path
        self.threshold = 0.7
        self.load_model()

    def load_model(self):
        try:
            self.nlp = spacy.load(self.model_path)
        except Exception as e:
            print(f"❌ Error cargando modelo spaCy: {e}")
            self.nlp = None

    def classify(self, text: str) -> tuple:
        if not self.nlp:
            return ("desconocido", 0.0)
        doc = self.nlp(text)
        if not doc.cats:
            return ("desconocido", 0.0)
        intent = max(doc.cats, key=doc.cats.get)
        confidence = doc.cats[intent]
        if confidence >= self.threshold:
            return (intent, confidence)
        else:
            return ("desconocido", confidence)

    def get_all_probabilities(self, text: str) -> dict:
        if not self.nlp:
            return {}
        doc = self.nlp(text)
        return dict(doc.cats) if doc.cats else {}
