
from .ml_intent_classifier import MLIntentClassifier
from .entity_extractor import EntityExtractor

class NLUProcessor:
    def __init__(self):
        self.intent_classifier = MLIntentClassifier()
        self.entity_extractor = EntityExtractor()
        # Intentar cargar modelo existente
        if not self.intent_classifier.load_model():
            print("🔄 Entrenando nuevo modelo...")
            self.intent_classifier.train_and_evaluate()

    def process(self, text: str) -> dict:
        intent, confidence = self.intent_classifier.classify(text)
        entities = self.entity_extractor.extract(text)
        return {
            'intent': intent,
            'confidence': confidence,
            'entities': entities,
            'requires_clarification': confidence < 0.7,
            'model_info': self.intent_classifier.get_model_info()
        }