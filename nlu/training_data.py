import json
import os


class TrainingDataset:
    def __init__(self):
        self.training_examples = {
            'buscar_producto': [
                'busco un celular Samsung',
                'quiero ver laptops',
                'mostrame televisores',
                'necesito una tablet',
                'buscar iPhone 15',
                'ver productos Apple',
                'mostrar smartphones',
                'busco auriculares',
                'necesito una computadora',
                'quiero comprar notebook'
            ],
            'recomendar_categoria': [
                'recomienda algo de electrónicos',
                'qué tienes en deportes',
                'sugiéreme productos para casa',
                'qué hay en libros',
                'recomienda ropa',
                'sugiere algo bueno',
                'qué me recomiendas',
                'mostrar categorías',
                'ver qué tienen',
                'opciones disponibles'
            ],
            'comparar_precios': [
                'compara precios del iPhone',
                'cuál es más barato',
                'buscar mejor precio',
                'comparar con otras tiendas',
                'encontrar más económico',
                'precio en otras páginas',
                'buscar ofertas',
                'ver descuentos',
                'comparar online',
                'mejor oferta disponible'
            ],
            'info_producto': [
                'información del producto',
                'detalles técnicos',
                'características completas',
                'especificaciones',
                'más información',
                'qué incluye',
                'garantía del producto',
                'opiniones del producto',
                'reseñas',
                'descripción completa'
            ],
            'saludo': [
                'hola',
                'buenos días',
                'buenas tardes',
                'hey',
                'saludos',
                'qué tal',
                'cómo estás',
                'hi',
                'hello',
                'buenas'
            ],
            'ayuda': [
                'ayuda',
                'help',
                'no entiendo',
                'cómo funciona',
                'qué puedo hacer',
                'opciones disponibles',
                'comandos',
                'instrucciones',
                'guía',
                'manual'
            ],
            'comparar_precios_web': [
                'comparar precios online',
                'buscar en otras tiendas',
                'precio en mercadolibre',
                'ver en falabella',
                'comparar con web',
                'buscar más barato online',
                'precio en internet',
                'ofertas en línea',
                'comparar tiendas online',
                'mejor precio web',
                '¿cuánto cuesta en otras páginas?',
                'compara precios en internet',
                '¿hay mejor precio fuera?',
                'buscar precio externo',
                'ver precios en otras plataformas',
                'compara con mercado libre',
                'compara con falabella',
                'precio fuera de la tienda',
                '¿hay ofertas en otros sitios?',
                'buscar precio alternativo',
                '¿hay mejores precios fuera de la tienda?',
                '¿dónde está más barato este producto?',
                '¿puedes comparar precios en otras tiendas?',
                '¿cuánto cuesta en MercadoLibre o Falabella?',
                'busca mejores ofertas en internet',
                '¿hay descuentos en otras páginas web?',
                'compara el precio con otras plataformas',
                '¿está más económico en otros sitios?',
                'revisa precios en tiendas online',
                '¿puedes buscar ofertas externas?',
                'ver si hay mejor precio afuera',
                '¿cuánto vale en otras tiendas online?',
                'buscar alternativas más baratas',
                '¿hay promociones en otros lugares?',
                'revisar precios en competencia',
                '¿está más barato en mercado libre?',
                '¿falabella tiene mejor precio?',
                'comparar con precios externos',
                '¿dónde puedo encontrarlo más económico?',
                'buscar ofertas en internet',
                '¿hay mejores deals online?',
                'ver precios en otras webs',
                '¿puedes comparar con sitios externos?',
                'revisar si hay mejor oferta fuera',
                '¿está más barato online?',
                'Desearía comparar precios en otras plataformas digitales',
                'Podría verificar precios en sitios externos',
                'a ver si está más barato en otro lado',
                'checa precios en otras páginas',
                'laptop más barata en mercadolibre',
                'iPhone 15 precio falabella vs aquí',
                'comparar presios online'
                'mercado libre tiene mejor precio?', 
            ],
        }

        json_path = "tools/tu_nuevo_dataset.json"
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    intent = item["intent"]
                    text = item["text"]
                    if intent not in self.training_examples:
                        self.training_examples[intent] = []
                    if text not in self.training_examples[intent]:
                        self.training_examples[intent].append(text)

    def get_training_data(self) -> tuple:
        texts = []
        labels = []
        for intent, examples in self.training_examples.items():
            for example in examples:
                texts.append(example)
                labels.append(intent)
        return texts, labels