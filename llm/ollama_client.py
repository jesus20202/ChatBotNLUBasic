from huggingface_hub import InferenceClient
from typing import Optional
import logging
import asyncio

logger = logging.getLogger("ollama_client")
logging.basicConfig(level=logging.INFO)

class OllamaClient:
    def __init__(self, model_name: str, api_key: str, max_retries: int = 3):
        self.client = InferenceClient(
            provider="groq",
            api_key=api_key
        )
        self.model_name = model_name
        self.max_retries = max_retries

    async def generate_response(self, prompt: str) -> str:
        for attempt in range(1, self.max_retries + 1):
            try:
                completion = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}]
                )
                logger.info(f"Respuesta generada exitosamente en el intento {attempt}")
                return completion.choices[0].message.content
            except Exception as e:
                logger.warning(f"Error en intento {attempt}: {e}")
                await asyncio.sleep(1 * attempt)
        logger.error("Fallaron todos los intentos de generar una respuesta")
        return "Error: No se pudo obtener respuesta del modelo"