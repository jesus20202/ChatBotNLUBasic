# Umbral mínimo de confianza para aceptar una intención
INTENT_THRESHOLD = 0.7

# Mapeo de etiquetas de entidades de spaCy a nombres internos
ENTITY_LABELS = {
    "PRODUCT": "categoria",
    "ORG": "marca",
    "MONEY": "rango_precio",
    "PERSON": "usuario"
}

# Ruta donde se guardará/cargará el modelo entrenado de spaCy
MODEL_PATH = "nlu/spacy_model/modelo_intenciones"

# Nombre del modelo base de spaCy para español
#BASE_SPACY_MODEL = "es_dep_news_trf"

# Lista de intenciones soportadas 
SUPPORTED_INTENTS = [
    "buscar_producto",
    "comparar_precios",
    "recomendar_categoria",
    "info_producto",
    "saludo",
    "ayuda",
    "comparar_precios_web"
]

