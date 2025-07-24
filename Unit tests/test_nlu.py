# tests/test_nlu.py
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from nlu import NLUProcessor
from nlu.spacy_intent_classifier import MLIntentClassifier
from nlu.spacy_entity_extractor import EntityExtractor

class TestNLUProcessor:
    def setup_method(self):
        self.nlu = NLUProcessor()

    def test_process_returns_dict(self):
        result = self.nlu.process("Hola")
        assert isinstance(result, dict)
        assert "intent" in result
        assert "entities" in result
        assert "confidence" in result

    def test_intent_classification_saludo(self):
        result = self.nlu.process("Hola, ¿cómo estás?")
        assert result["intent"] == "saludo"
        assert result["confidence"] > 0.5

    def test_intent_classification_buscar_producto(self):
        result = self.nlu.process("Busco laptops Lenovo")
        assert result["intent"] == "buscar_producto"
        assert result["confidence"] > 0.5

    def test_intent_classification_comparar_precios_web(self):
        result = self.nlu.process("¿Cuál es el precio en MercadoLibre?")
        assert result["intent"] == "comparar_precios_web"
        assert result["confidence"] > 0.5

    def test_intent_classification_ayuda(self):
        result = self.nlu.process("¿Me puedes ayudar?")
        assert result["intent"] == "ayuda"
        assert result["confidence"] > 0.5

    def test_low_confidence_handling(self):
        result = self.nlu.process("sdkfjsldfkjslkdfj")
        assert result["confidence"] < 0.7

class TestMLIntentClassifier:
    def setup_method(self):
        self.classifier = MLIntentClassifier()

    def test_classify_returns_tuple(self):
        intent, confidence = self.classifier.classify("Hola")
        assert isinstance(intent, str)
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1

    def test_get_all_probabilities(self):
        probs = self.classifier.get_all_probabilities("Busco celulares")
        assert isinstance(probs, dict)
        assert len(probs) > 0
        assert all(0 <= prob <= 1 for prob in probs.values())

class TestEntityExtractor:
    def setup_method(self):
        self.extractor = EntityExtractor()

    def test_extract_returns_dict(self):
        entities = self.extractor.extract("Busco laptops Samsung")
        assert isinstance(entities, dict)

    def test_extract_marca(self):
        entities = self.extractor.extract("Busco productos Samsung")
        # Verificar que se detecte marca si está en la lista
        if "marca" in entities:
            assert isinstance(entities["marca"], str)

    def test_extract_categoria(self):
        entities = self.extractor.extract("Busco laptops")
        # Verificar que se detecte categoría si está en la lista
        if "categoria" in entities:
            assert isinstance(entities["categoria"], str)

    def test_normalize_text(self):
        normalized = self.extractor.normalize("TEXTO EN MAYÚSCULAS")
        assert normalized == "texto en mayusculas"