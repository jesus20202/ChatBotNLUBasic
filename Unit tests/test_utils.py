# tests/test_utils.py
import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.utils_chat import extract_product_name

class TestUtilsChat:
    
    def test_extract_product_name_with_marca_and_categoria(self):
        entities = {"marca": "Samsung", "categoria": "celular"}
        result = extract_product_name("mensaje", entities)
        
        assert "Samsung" in result
        assert "celular" in result

    def test_extract_product_name_only_marca(self):
        entities = {"marca": "Apple"}
        result = extract_product_name("mensaje", entities)
        
        assert "Apple" in result

    def test_extract_product_name_only_categoria_string(self):
        entities = {"categoria": "laptop"}
        result = extract_product_name("mensaje", entities)
        
        assert "laptop" in result

    @patch('database.connection.get_db')
    def test_extract_product_name_categoria_id(self, mock_get_db):
        # Mock de la base de datos
        mock_db = Mock()
        mock_get_db.return_value.__next__.return_value = mock_db
        
        mock_categoria = Mock()
        mock_categoria.nombre = "electronica"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_categoria
        
        entities = {"categoria": 1}
        result = extract_product_name("mensaje", entities)
        
        assert "electronica" in result

    @patch('database.connection.get_db')
    def test_extract_product_name_categoria_id_not_found(self, mock_get_db):
        # Mock de la base de datos sin resultado
        mock_db = Mock()
        mock_get_db.return_value.__next__.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        entities = {"categoria": 999}
        result = extract_product_name("mensaje de prueba", entities)
        
        # Debería retornar el mensaje original si no encuentra la categoría
        assert result == "mensaje de prueba"

    def test_extract_product_name_no_entities(self):
        entities = {}
        message = "busco algo interesante"
        result = extract_product_name(message, entities)
        
        assert result == message

    def test_extract_product_name_empty_entities(self):
        entities = {"categoria": "", "marca": ""}
        message = "mensaje original"
        result = extract_product_name(message, entities)
        
        assert result == message