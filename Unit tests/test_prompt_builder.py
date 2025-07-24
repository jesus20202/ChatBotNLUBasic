# tests/test_prompt_builder.py
import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.prompt_builder import PromptBuilder
from unittest.mock import Mock

class TestPromptBuilder:
    def setup_method(self):
        self.builder = PromptBuilder()

    def test_build_context_buscar_producto(self):
        entities = {"marca": "Samsung", "categoria": "celular"}
        db_results = []
        
        context = self.builder.build_context("buscar_producto", entities, db_results)
        
        assert isinstance(context, str)
        assert "Samsung" in context
        assert "celular" in context
        assert "buscando productos" in context

    def test_build_context_saludo(self):
        entities = {}
        db_results = []
        
        context = self.builder.build_context("saludo", entities, db_results)
        
        assert isinstance(context, str)
        assert "saludando" in context
        assert "amigable" in context

    def test_build_context_ayuda(self):
        entities = {}
        db_results = []
        
        context = self.builder.build_context("ayuda", entities, db_results)
        
        assert isinstance(context, str)
        assert "ayuda" in context
        assert "funciones" in context

    def test_build_context_comparar_precios_web_with_comparison(self):
        entities = {"categoria": "laptop"}
        db_results = []
        comparison = {
            "analysis": {
                "status": "success",
                "best_deal": {
                    "title": "Laptop HP",
                    "price": 1500.00
                },
                "db_comparison": {
                    "savings_vs_min": 200.00
                }
            }
        }
        
        context = self.builder.build_context("comparar_precios_web", entities, db_results, comparison)
        
        assert isinstance(context, str)
        assert "Laptop HP" in context
        assert "1500" in context
        assert "200" in context

    def test_build_context_with_db_results(self):
        entities = {"marca": "Apple"}
        # Mock productos
        mock_producto = Mock()
        mock_producto.nombre = "iPhone 15"
        mock_producto.marca = "Apple"
        mock_producto.precio = 999.99
        mock_producto.stock = 10
        db_results = [mock_producto]
        
        context = self.builder.build_context("buscar_producto", entities, db_results)
        
        assert isinstance(context, str)
        assert "iPhone 15" in context
        assert "Apple" in context
        assert "999.99" in context
        assert "10 unidades" in context

    def test_build_context_no_db_results(self):
        entities = {"marca": "Desconocida"}
        db_results = []
        
        context = self.builder.build_context("buscar_producto", entities, db_results)
        
        assert isinstance(context, str)
        assert "No se encontraron productos" in context

    def test_build_context_unknown_intent(self):
        entities = {}
        db_results = []
        
        context = self.builder.build_context("unknown_intent", entities, db_results)
        
        assert isinstance(context, str)
        assert "unknown_intent" in context
        assert "útil" in context

    def test_build_fallback_prompt(self):
        fallback = self.builder.build_fallback_prompt("mensaje confuso", "unknown", 0.3)
        
        assert isinstance(fallback, str)
        assert "mensaje confuso" in fallback
        assert "0.30" in fallback
        assert "ejemplos" in fallback