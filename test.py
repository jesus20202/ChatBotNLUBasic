
import os
from dotenv import load_dotenv       
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise RuntimeError(
        "No se encontró HF_TOKEN en las variables de entorno. "
    )

client = InferenceClient(
    provider="groq",           
    api_key=HF_TOKEN,
)
completion = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3-8B-Instruct",
    messages=[
        {"role": "user", "content": "¿Cúal es la velocidad de la luz?"}
    ],
)

print("Modelo:", completion.choices[0].message.content)
