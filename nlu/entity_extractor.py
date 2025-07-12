import re
import unicodedata

class EntityExtractor:
    def __init__(self):
        # Listas de ejemplo, puedes poblarlas desde la BD si lo prefieres
        self.marcas = [
            "alphatech", "ultrapc", "soundmax", "fittime", "modaclásica", "denimpro", "rainwear",
            "cleanbot", "brewmaster", "lighthome", "trailx", "fitgear", "proleague", "techbooks",
            "gourmetlibros", "lectora", "eleganceco", "beautyplus", "makeart", "visiontech",
            "keymaster", "ergomouse", "curveview", "summerstyle", "runfast", "leatherline",
            "sleepwell", "homevoice", "thermomax", "prospin", "yogaflex", "smartfit", "futurbooks",
            "greenguide", "fotolibro", "skinpure", "beautymask", "nailart", "turbodry", "camvision"
        ]
        self.categorias = ["electronica", "ropa", "deporte", "libros", "belleza"]

    def normalize(self, text: str) -> str:
        text = text.lower()
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def extract(self, text: str) -> dict:
        text_norm = self.normalize(text)
        entidades = {}

        # Marca
        for marca in self.marcas:
            if marca in text_norm:
                entidades["marca"] = marca
                break

        # Categoría
        for categoria in self.categorias:
            if categoria in text_norm:
                entidades["categoria"] = categoria
                break

        # Rango de precio (ejemplo: "entre 100 y 500", "menos de 300", "mayor a 1000")
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

        # Características específicas (ejemplo: "pantalla grande", "doble sim")
        # ...existing code...

        # Características específicas
        lista_caracteristicas = [
            "pantalla grande", "doble sim", "resistente al agua",
            "bateria larga", "camara buena"
        ]
        patron = r'(' + '|'.join(map(re.escape, lista_caracteristicas)) + r')'
        caracteristicas = re.findall(patron, text_norm)
        if caracteristicas:
            entidades["caracteristicas"] = caracteristicas

        return entidades