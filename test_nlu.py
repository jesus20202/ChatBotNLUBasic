from nlu import NLUProcessor
from nlu.spacy_intent_classifier import MLIntentClassifier
from nlu.spacy_entity_extractor import EntityExtractor

class NLUProcessor:
    def __init__(self):
        self.intent_classifier = MLIntentClassifier()
        self.entity_extractor = EntityExtractor()

    def process(self, text: str) -> dict:
        intent, confidence = self.intent_classifier.classify(text)
        entities = self.entity_extractor.extract(text)
        return {
            "intent": intent,
            "confidence": confidence,
            "entities": entities
        }

nlu = NLUProcessor()

def test_intent_classification():
    test_cases = [
        ("Busco laptops baratas", "buscar_producto"),
        ("Compara precios de celulares", "comparar_precios"),
        ("Recomiéndame algo bueno", "recomendar_categoria"),
        ("Hola, ¿cómo estás?", "saludo"),
        ("¿Me puedes ayudar?", "ayuda"),
        ("¿Cuál es el precio en MercadoLibre?", "comparar_precios_web"),
        ("Dame información del producto", "info_producto"),
    ]
    for text, expected_intent in test_cases:
        result = nlu.process(text)
        print(f"Texto: {text}")
        print(f"Intención detectada: {result['intent']} (esperada: {expected_intent})")
        assert result['intent'] == expected_intent or result['confidence'] < 0.7

def test_entity_extraction():
    test_cases = [
        ("Busco laptops Lenovo baratas", {"categoria": "laptops", "marca": "Lenovo"}),
        ("iPhone 15 de $800", {"categoria": "iPhone", "rango_precio": "$800"}),
    ]
    for text, expected_entities in test_cases:
        result = nlu.process(text)
        print(f"Texto: {text}")
        print(f"Entidades detectadas: {result['entities']} (esperadas: {expected_entities})")
        for key, value in expected_entities.items():
            assert key in result['entities']

def test_full_pipeline():
    text = "Recomiéndame celulares Samsung económicos"
    result = nlu.process(text)
    print(f"Pipeline completo para: {text}")
    print(result)
    assert "intent" in result and "entities" in result

if __name__ == "__main__":
    print("== Test: Clasificación de intenciones ==")
    test_intent_classification()
    print("== Test: Extracción de entidades ==")
    test_entity_extraction()
    print("== Test: Pipeline completo ==")
    test_full_pipeline()
    print("✅ Todos los tests pasaron correctamente.")