from sqlalchemy.orm import Session
from models.database import Producto, Categoria
from typing import List, Optional




class FuncionesCRUD: 
    def __init__(self,db: Session):
        self.db = db

    def listar_productos(self):
        return self.db.query(Producto).all()
    
    def get_categoria_id(self, nombre_categoria: str) -> Optional[int]:
        categoria = self.db.query(Categoria).filter(Categoria.nombre.ilike(nombre_categoria)).first()
        return categoria.id if categoria else None
    
    def search_by_intent(self, intent: str, entities: dict) -> list:
        query = self.db.query(Producto)

        working_entities = entities.copy()

        if "categoria" in entities and isinstance(entities["categoria"], str):
            categoria_id = self.get_categoria_id(entities["categoria"])
            entities["categoria"] = categoria_id

        # Filtros dinámicos según intención y entidades
        if intent == "buscar_producto":
            if "marca" in entities:
                query = query.filter(Producto.marca.ilike(f"%{entities['marca']}%"))
            if "categoria" in entities and entities["categoria"]:
                query = query.filter(Producto.categoria_id == entities["categoria"])
            if "rango_precio" in entities:
                rp = entities["rango_precio"]
                if "min" in rp:
                    query = query.filter(Producto.precio >= rp["min"])
                if "max" in rp:
                    query = query.filter(Producto.precio <= rp["max"])
            if "caracteristicas" in entities:
                for car in entities["caracteristicas"]:
                    query = query.filter(Producto.descripcion.ilike(f"%{car}%"))
            return query.all()

        elif intent == "recomendar_categoria":
            if "categoria" in entities and entities["categoria"]:
                query = query.filter(Producto.categoria_id == entities["categoria"])
            return query.order_by(Producto.precio.desc()).limit(5).all()

        elif intent == "comparar_precios":
            if "marca" in entities:
                query = query.filter(Producto.marca.ilike(f"%{entities['marca']}%"))
            if "categoria" in entities and entities["categoria"]:
                query = query.filter(Producto.categoria_id == entities["categoria"])
            return query.order_by(Producto.precio.asc()).limit(5).all()

        elif intent == "info_producto":
            if "marca" in entities:
                query = query.filter(Producto.marca.ilike(f"%{entities['marca']}%"))
            if "categoria" in entities and entities["categoria"]:
                query = query.filter(Producto.categoria_id == entities["categoria"])
            return query.all()

        # Fallback: retorna todos los productos activos
        return query.filter(Producto.activo == True).limit(10).all()

    def get_recommendations(self, categoria: str, limit: int = 5):
        return self.db.query(Producto).filter(
            Producto.categoria_id == categoria,
            Producto.activo == True
        ).order_by(Producto.precio.desc()).limit(limit).all()

    def compare_prices(self, entities: dict):
        query = self.db.query(Producto)
        if "marca" in entities:
            query = query.filter(Producto.marca.ilike(f"%{entities['marca']}%"))
        if "categoria" in entities:
            query = query.filter(Producto.categoria_id == entities["categoria"])
        return query.order_by(Producto.precio.asc()).limit(5).all()