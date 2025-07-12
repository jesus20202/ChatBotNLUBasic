import re
import unicodedata

class IntentClassifier:
    def __init__(self):
        self.patterns = {
            'buscar_producto': ['buscar', 'encontrar', 'mostrar', 'ver', 'busco', 'deseo ver'],
            'recomendar_categoria': ['recomendar', 'sugerir', 'qué hay', 'mejor categoría'],
            'comparar_precios': ['comparar', 'precio', 'más barato', 'diferencia de precio'],
            'info_producto': ['información', 'detalles', 'características', 'cuéntame de'],
            'saludo': ['hola', 'buenos días', 'hey', 'buenas'],
            'ayuda': ['ayuda', 'help', 'no entiendo', 'cómo funciona']
        }

    def normalize(self, text: str) -> str:
        text = text.lower()
        text = unicodedata.normalize('NFD', text)
        text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def classify(self, text: str) -> tuple[str, float]:
        text_norm = self.normalize(text)
        for intent, keywords in self.patterns.items():
            for kw in keywords:
                kw_norm = self.normalize(kw)
                if re.search(rf'\b{re.escape(kw_norm)}\b', text_norm):
                    return intent, 1.0
                elif kw_norm in text_norm:
                    return intent, 0.7
        return "desconocido", 0.0