from nlu.spacy_intent_classifier import MLIntentClassifier
from nlu.spacy_entity_extractor import EntityExtractor
import logging

class NLUProcessor:
    def __init__(self):
        self.intent_classifier = MLIntentClassifier()
        self.entity_extractor = EntityExtractor() 
        self.logger = self.setup_logger()

    def setup_logger(self):
        logger = logging.getLogger('nlu')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def process(self, text: str) -> dict:
        try:
            intent, confidence = self.intent_classifier.classify(text)
            entities = self.entity_extractor.extract(text)
            self.logger.info(f"Intent: {intent} (conf: {confidence:.2f}) | Entities: {entities}")
            # Fallback si la confianza es baja
            if confidence < self.intent_classifier.threshold:
                return self.fallback_processing(text, entities)
            return {
                "intent": intent,
                "confidence": confidence,
                "entities": entities
            }
        except Exception as e:
            self.logger.error(f"Error en NLUProcessor: {e}")
            return self.fallback_processing(text, {})

    def fallback_processing(self, text: str, entities: dict) -> dict:
        # Aquí puedes integrar un fallback al LLM o reglas simples
        self.logger.warning("Usando fallback NLU (intención desconocida)")
        return {
            "intent": "desconocido",
            "confidence": 0.0,
            "entities": entities
        }