# Chatbot IA para E-commerce

Este proyecto es un chatbot inteligente en español diseñado para asistir a usuarios en tareas de búsqueda, comparación y recomendación de productos en una tienda online. Utiliza procesamiento de lenguaje natural (NLU) con spaCy para entender intenciones y extraer entidades, y se apoya en modelos LLM para respuestas avanzadas. Incluye frontend web, API REST y soporte para WebSockets.

---

## Características principales

- **Procesamiento de lenguaje natural (NLU):** Clasificación de intenciones y extracción de entidades relevantes (marca, categoría, precio, usuario) usando spaCy.
- **Respuestas enriquecidas:** Generación de respuestas contextuales usando modelos LLM (por ejemplo, Llama 3 vía Hugging Face).
- **Consultas dinámicas a base de datos:** Búsqueda y comparación de productos en una base de datos relacional.
- **Interfaz web interactiva:** Chat en tiempo real con WebSockets y frontend moderno.
- **API RESTful:** Endpoints para integración con otros sistemas o pruebas automáticas.
- **Entrenamiento y mejora continua:** Scripts y utilidades para crear y mejorar los datos de entrenamiento del modelo NLU.

---

## Estructura del proyecto

```
main.py                  # Aplicación principal FastAPI
database/                # Conexión y consultas a la base de datos
llm/                     # Cliente LLM y construcción de prompts
models/                  # Modelos y esquemas de datos (ORM)
nlu/                     # Procesamiento NLU (intenciones y entidades)
static/                  # Archivos estáticos (JS, CSS)
templates/               # Plantillas HTML para el frontend
websockets_file/         # Gestión de conexiones WebSocket
Unit tests/              # Pruebas unitarias
tools/                   # Scripts para generación/augmentación de datos de entrenamiento
```

---

## Instalación y configuración

### 1. Clonar el repositorio

```sh
git clone <URL-del-repo>
cd <nombre-del-proyecto>
```

### 2. Instalar dependencias

Asegúrate de tener Python 3.10+ y pip. Instala los paquetes necesarios:

```sh
pip install -r requirements.txt
```

**Dependencias clave:**  
- fastapi  
- uvicorn  
- sqlalchemy  
- spacy  
- googletrans  
- huggingface_hub

### 3. Configurar variables de entorno

Crea un archivo `.env` con tus credenciales y configuración de base de datos y API LLM. Ejemplo:

```
DATABASE_URL=postgresql://usuario:password@localhost:5432/tu_db
HF_TOKEN=tu_token_huggingface
```

### 4. Inicializar la base de datos

Crea las tablas usando los scripts en [`tablas.txt`](tablas.txt) o ejecuta las migraciones si tienes un sistema de migración.

---

## Ejecución del chatbot

### 1. Iniciar la aplicación

```sh
uvicorn main:app --reload
```

### 2. Acceder al frontend

Abre tu navegador en [http://localhost:8000](http://localhost:8000) para usar la interfaz de chat.

### 3. Probar la API

Puedes usar herramientas como Postman o curl para probar los endpoints principales:

- `POST /chat` — Envía un mensaje y recibe respuesta del chatbot.
- `GET /productos` — Lista productos disponibles.
- `GET /categorias` — Lista categorías de productos.

---

## Entrenamiento y mejora del modelo NLU

El chatbot utiliza un modelo spaCy entrenado para clasificar intenciones y extraer entidades. El modelo y los datos de entrenamiento se encuentran en la carpeta [`nlu/`](nlu/).

### ¿Cuándo es necesario reentrenar?

- Si agregas nuevas intenciones o ejemplos de entrenamiento.
- Si quieres mejorar la precisión del modelo con más datos.
- Si actualizas la estructura de las entidades.

### ¿Cómo reentrenar el modelo?

1. **Edita o amplía los datos de entrenamiento:**  
   Los ejemplos están en [`nlu/training/training_data.json`](nlu/training/training_data.json) .

2. **Ejecuta el script de entrenamiento:**  
   Desde la raíz del proyecto:

   ```sh
   python nlu/training/train_intent_classifier.py
   ```

   Esto entrenará el modelo y lo guardará en [`nlu/spacy_model/modelo_intenciones/`](nlu/spacy_model/modelo_intenciones/).

3. **Reinicia la aplicación:**  
   Para que el chatbot use el nuevo modelo, reinicia el servidor FastAPI.


---

## Personalización y ampliación

- **Agregar nuevas intenciones:**  
  Añade ejemplos en el archivo de entrenamiento y actualiza la lógica en el NLU si es necesario.
- **Mejorar extracción de entidades:**  
  Modifica los extractores en [`nlu/spacy_entity_extractor.py`](nlu/spacy_entity_extractor.py) o [`nlu/entity_extractor.py`](nlu/entity_extractor.py).
- **Cambiar el modelo LLM:**  
  Edita la configuración en [`llm/ollama_client.py`](llm/ollama_client.py) y las variables de entorno.

---


