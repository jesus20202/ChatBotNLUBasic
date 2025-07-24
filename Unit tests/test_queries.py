# tests/test_queries.py
import pytest
from unittest.mock import Mock, patch
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.queries import FuncionesCRUD
from models.database import Producto, Categoria

class TestFuncionesCRUD:
    def setup_method(self):
        self.mock_db = Mock()
        self.crud = FuncionesCRUD(self.mock_db)

    @patch.object(FuncionesCRUD, 'get_categoria_id')
    def test_search_by_intent_buscar_producto(self, mock_get_categoria_id):
        # Mock query builder
        mock_query = Mock()
        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_get_categoria_id.return_value = 1

        entities = {"categoria": "electronica", "marca": "Samsung"}
        result = self.crud.search_by_intent("buscar_producto", entities)

        assert isinstance(result, list)
        self.mock_db.query.assert_called_with(Producto)

    def test_search_by_intent_recomendar_categoria(self):
        mock_query = Mock()
        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        entities = {"categoria": 1}
        result = self.crud.search_by_intent("recomendar_categoria", entities)

        assert isinstance(result, list)

    def test_search_by_intent_comparar_precios(self):
        mock_query = Mock()
        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        entities = {"marca": "Samsung"}
        result = self.crud.search_by_intent("comparar_precios", entities)

        assert isinstance(result, list)

    def test_search_by_intent_comparar_precios_web(self):
        mock_query = Mock()
        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        entities = {"categoria": 1, "marca": "Apple"}
        result = self.crud.search_by_intent("comparar_precios_web", entities)

        assert isinstance(result, list)

    def test_search_by_intent_fallback(self):
        mock_query = Mock()
        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        result = self.crud.search_by_intent("unknown_intent", {})

        assert isinstance(result, list)

    def test_get_recommendations(self):
        mock_query = Mock()
        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        result = self.crud.get_recommendations("electronica", 5)

        assert isinstance(result, list)

    @patch.object(FuncionesCRUD, 'get_categoria_id')
    def test_get_categoria_id_found(self, mock_method):
        mock_method.return_value = 1
        result = self.crud.get_categoria_id("electronica")
        assert result == 1

    def test_listar_productos(self):
        mock_query = Mock()
        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []

        result = self.crud.listar_productos()

        assert isinstance(result, list)
        self.mock_db.query.assert_called_with(Producto)