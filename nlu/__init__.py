from nlu.intent_classifier import IntentClassifier
from nlu.entity_extractor import EntityExtractor

class NLUProcessor:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()

    def process(self, text: str) -> dict:
        intent, confidence = self.intent_classifier.classify(text)
        entities = self.entity_extractor.extract(text)
        return {
            "intent": intent,
            "confidence": confidence,
            "entities": entities
        }