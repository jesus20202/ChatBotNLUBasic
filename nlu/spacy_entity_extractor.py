import re
import unicodedata
from database.connection import get_db
from models.database import Categoria, Producto

class EntityExtractor:
    def __init__(self):
        # Cargar listas dinámicamente desde la BD
        self.marcas = self._load_marcas_from_db()
        self.categorias = self._load_categorias_from_db()

    def _load_marcas_from_db(self) -> list:
        """Cargar marcas únicas desde la BD"""
        try:
            db = next(get_db())
            marcas = db.query(Producto.marca).filter(
                Producto.marca.isnot(None),
                Producto.activo == True
            ).distinct().all()
            return [marca[0].lower() for marca in marcas if marca[0]]
        except Exception as e:
            print(f"Error cargando marcas: {e}")
            # Fallback a lista básica
            return ["lenovo", "samsung", "apple", "xiaomi"]

    def _load_categorias_from_db(self) -> list:
        """Cargar categorías desde la BD"""
        try:
            db = next(get_db())
            categorias = db.query(Categoria.nombre).filter(
                Categoria.activo == True
            ).all()
            # Incluir variantes comunes
            categorias_list = []
            for cat in categorias:
                nombre = cat[0].lower()
                categorias_list.append(nombre)
                # Agregar variantes comunes
                if "electronica" in nombre:
                    categorias_list.extend(["laptop", "laptops", "celular", "celulares", "tablet", "tablets"])
            return list(set(categorias_list))
        except Exception as e:
            print(f"Error cargando categorías: {e}")
            # Fallback a lista básica
            return ["electronica", "ropa", "deporte", "libros", "belleza"]

    def refresh_entities(self):
        """Refrescar listas desde la BD (útil para actualizaciones)"""
        self.marcas = self._load_marcas_from_db()
        self.categorias = self._load_categorias_from_db()

    def normalize(self, text: str) -> str:
        text = text.lower()
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def extract(self, text: str) -> dict:
        text_norm = self.normalize(text)
        entidades = {}

        # Marca (desde BD)
        for marca in self.marcas:
            if marca in text_norm:
                entidades["marca"] = marca
                break

        # Categoría (desde BD + variantes)
        for categoria in self.categorias:
            if categoria in text_norm:
                entidades["categoria"] = categoria
                break

        # Rango de precio (mantienes la lógica actual)
        rango_precio = re.search(r'(\d{2,6})\s*(a|hasta|-|y)\s*(\d{2,6})', text_norm)
        if rango_precio:
            entidades["rango_precio"] = {
                "min": int(rango_precio.group(1)),
                "max": int(rango_precio.group(3))
            }
        else:
            menor = re.search(r'menos de (\d{2,6})', text_norm)
            mayor = re.search(r'mayor a (\d{2,6})', text_norm)
            if menor:
                entidades["rango_precio"] = {"max": int(menor.group(1))}
            if mayor:
                entidades["rango_precio"] = {"min": int(mayor.group(1))}

        # Características específicas (mantienes la lógica actual)
        lista_caracteristicas = [
            "pantalla grande", "doble sim", "resistente al agua",
            "bateria larga", "camara buena"
        ]
        patron = r'(' + '|'.join(map(re.escape, lista_caracteristicas)) + r')'
        caracteristicas = re.findall(patron, text_norm)
        if caracteristicas:
            entidades["caracteristicas"] = caracteristicas

        return entidades