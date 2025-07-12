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
from nlu.intent_classifier import IntentClassifier
from fastapi.templating import Jinja2Templates

from llm.prompt_builder import PromptBuilder
from nlu import NLUProcessor
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

manager = ConnectionManager()

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
    classifier = IntentClassifier()
    intent, confidence = classifier.classify(text)
    return {"text": text, "intent": intent, "confidence": confidence}

@app.post("/chat")
async def chat_endpoint(message: str = Body(..., embed=True), session_id: str = Body(None, embed=True), db: Session = Depends(get_db)):
    # 1. Procesar con NLU
    nlu = NLUProcessor()
    nlu_result = nlu.process(message)
    intent = nlu_result["intent"]
    entities = nlu_result["entities"]

    # 2. Consultar BD
    crud = FuncionesCRUD(db)
    productos = crud.search_by_intent(intent, entities)

    # 3. Construir prompt
    prompt_builder = PromptBuilder()
    prompt = prompt_builder.build_context(intent, entities, productos)

    # 4. Llamar LLM
    HF_TOKEN = os.getenv("HF_TOKEN")
    MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"
    client = OllamaClient(model_name=MODEL_NAME, api_key=HF_TOKEN)
    respuesta = await client.generate_response(prompt)

    # 5. Guardar en BD (opcional, ejemplo)
    # Aquí podrías guardar la conversación en la tabla correspondiente

    # 6. Retornar respuesta
    return {
        "message": message,
        "intent": intent,
        "entities": entities,
        "productos": [p.nombre for p in productos],
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
            # Procesar mensaje con NLU y BD
            nlu = NLUProcessor()
            nlu_result = nlu.process(data)
            intent = nlu_result["intent"]
            entities = nlu_result["entities"]

            # Consultar BD
            db = next(get_db())
            crud = FuncionesCRUD(db)
            productos = crud.search_by_intent(intent, entities)

            # Construir prompt y llamar LLM
            prompt_builder = PromptBuilder()
            prompt = prompt_builder.build_context(intent, entities, productos)
            HF_TOKEN = os.getenv("HF_TOKEN")
            MODEL_NAME = "meta-llama/Meta-Llama-3-8B-Instruct"
            client = OllamaClient(model_name=MODEL_NAME, api_key=HF_TOKEN)
            respuesta = await client.generate_response(prompt)

            # Enviar respuesta al cliente
            await manager.send_message(respuesta, session_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)