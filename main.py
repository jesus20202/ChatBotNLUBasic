from fastapi import FastAPI, Depends, Body ,WebSocket, WebSocketDisconnect
from websockets_file.manager import ConnectionManager
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database.connection import get_db
from models.database import Producto,Categoria
from models.schemas import ProductoOut
from database.queries import FuncionesCRUD
from fastapi import Request
from llm.ollama_client import OllamaClient
from fastapi.templating import Jinja2Templates
from scraping.price_comparator import PriceComparator
from llm.prompt_builder import PromptBuilder
from llm.utils_chat import extract_product_name
from nlu import NLUProcessor
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

nlu_processor = NLUProcessor()
manager = ConnectionManager()
price_comparator = PriceComparator()
nlu_processor = NLUProcessor()
prompt_builder = PromptBuilder()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#server de archivos estticos
app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/productos", response_model = list[ProductoOut])
def listar_productos(db: Session = Depends(get_db)):
    crud = FuncionesCRUD(db)
    return crud.listar_productos()


@app.post("/test-llm")
async def test_llm(prompt: str = Body(..., embed=True)):
    HF_TOKEN = os.getenv("HF_TOKEN")
    MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"
    client = OllamaClient(model_name=MODEL_NAME, api_key=HF_TOKEN)
    response = await client.generate_response(prompt)
    return {"prompt": prompt, "response": response}


@app.post("/test-intent")
def test_intent(text: str = Body(..., embed=True)):
    result = nlu_processor.process(text)
    return {"text": text, "intent": result["intent"], "confidence": result["confidence"]}

@app.post("/chat")
async def chat_endpoint(
    message: str = Body(..., embed=True),
    session_id: str = Body(None, embed=True),
    db: Session = Depends(get_db)
):
    nlu_result = nlu_processor.process(message)
    intent = nlu_result["intent"]
    entities = nlu_result["entities"]
    confidence = nlu_result["confidence"]

    intenciones_que_necesitan_entidades = ["buscar_producto", "comparar_precios", "comparar_precios_web", "info_producto"]
    
    if not entities and intent in intenciones_que_necesitan_entidades:
        return {
            "response": "No pude identificar la marca o categoría en tu mensaje. ¿Puedes especificar qué buscas?",
            "intent": intent,
            "entities": entities
        }

    # Fallback si la confianza es baja
    if confidence < 0.7:
        respuesta = "No estoy seguro de la intención de tu mensaje. ¿Podrías reformularlo o darme más detalles?"
        productos = []
    else:
        crud = FuncionesCRUD(db)
        productos = crud.search_by_intent(intent, entities)

        # Si es comparar precios web, activa scraping y contexto enriquecido
        if intent == "comparar_precios_web":
            product_name = extract_product_name(message, entities)  # Usar entities original
            crud = FuncionesCRUD(db)
            productos = crud.search_by_intent(intent, entities)
            db_price = float(productos[0].precio) if productos else None
            comparison = await price_comparator.compare_prices(product_name, db_price)
            prompt = prompt_builder.build_context(intent, entities, productos, comparison)
        else:
            crud = FuncionesCRUD(db)
            productos = crud.search_by_intent(intent, entities)
            prompt = prompt_builder.build_context(intent, entities, productos)

        HF_TOKEN = os.getenv("HF_TOKEN")
        MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"
        client = OllamaClient(model_name=MODEL_NAME, api_key=HF_TOKEN)
        respuesta = await client.generate_response(prompt)

    return {
        "message": message,
        "intent": intent,
        "confidence": confidence,
        "entities": entities,
        "productos": [p.nombre for p in productos] if confidence >= 0.7 else [],
        "respuesta": respuesta
    }

@app.get("/categorias")
def listar_categorias(db: Session = Depends(get_db)):
    categorias = db.query(Categoria).all()
    return [{"id": c.id, "nombre": c.nombre, "descripcion": c.descripcion} for c in categorias]

@app.get("/productos/{categoria}")
def productos_por_categoria(categoria: str, db: Session = Depends(get_db)):
    crud = FuncionesCRUD(db)
    categoria_id = crud.get_categoria_id(categoria)
    if not categoria_id:
        return []
    productos = db.query(Producto).filter(Producto.categoria_id == categoria_id).all()
    return [{"id": p.id, "nombre": p.nombre, "precio": float(p.precio), "marca": p.marca} for p in productos]

@app.get("/stats")
def stats(db: Session = Depends(get_db)):
    total_productos = db.query(Producto).count()
    total_categorias = db.query(Categoria).count()
    return {
        "total_productos": total_productos,
        "total_categorias": total_categorias
    }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            
            nlu_result = nlu_processor.process(data)
            intent = nlu_result["intent"]
            entities = nlu_result["entities"]
            confidence = nlu_result["confidence"]

            # ✅ MISMA lógica de fallback que REST
            intenciones_que_necesitan_entidades = ["buscar_producto", "comparar_precios", "comparar_precios_web", "info_producto"]
            
            if not entities and intent in intenciones_que_necesitan_entidades:
                respuesta = "No pude identificar la marca o categoría en tu mensaje. ¿Puedes especificar qué buscas?"
                await manager.send_message(respuesta, session_id)  # ✅ Parámetros correctos
                continue

            if confidence < 0.7:
                respuesta = "No estoy seguro de la intención de tu mensaje. ¿Podrías reformularlo?"
                await manager.send_message(respuesta, session_id)  # ✅ Parámetros correctos
                continue

            # Resto del flujo igual que /chat
            db = next(get_db())
            crud = FuncionesCRUD(db)
            productos = crud.search_by_intent(intent, entities)

            if intent == "comparar_precios_web":
                product_name = extract_product_name(data, entities)  # Usar entities original
                crud = FuncionesCRUD(db)
                productos = crud.search_by_intent(intent, entities)
                db_price = float(productos[0].precio) if productos else None
                comparison = await price_comparator.compare_prices(product_name, db_price)
                prompt = prompt_builder.build_context(intent, entities, productos, comparison)
            else:
                crud = FuncionesCRUD(db)
                productos = crud.search_by_intent(intent, entities)
                prompt = prompt_builder.build_context(intent, entities, productos)

            HF_TOKEN = os.getenv("HF_TOKEN")
            MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"
            client = OllamaClient(model_name=MODEL_NAME, api_key=HF_TOKEN)
            respuesta = await client.generate_response(prompt)

            await manager.send_message(respuesta, session_id)  # ✅ Parámetros correctos
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)

@app.post("/compare-prices")
async def compare_prices_endpoint(
    product_name: str = Body(..., embed=True),
    db_price: float = Body(None, embed=True)
):
    """Endpoint para comparar precios"""
    try:
        result = await price_comparator.compare_prices(product_name, db_price)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.get("/nlu-info")
async def nlu_info():
    """Información del modelo NLU"""
    return nlu_processor.intent_classifier.get_model_info()