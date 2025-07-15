import pandas as pd
from googletrans import Translator
import json
import re
import time
import random

# Mapeo de intenciones - Ajustado según el dataset real
INTENT_MAP = {
    "set": "configurar_alarma",
    "volume_mute": "silenciar_audio",
    "greet": "saludo",
    "help": "ayuda",
    "query": "buscar_producto",
    "stock": "info_producto",
    "definition": "info_producto",
    "factoid": "info_producto",
    "affirm": "saludo",
    "explain": "ayuda",
    "repeat": "ayuda"
}

# Función para limpiar anotaciones tipo [entity : value]
def remove_annotations(text):
    if isinstance(text, str):
        return re.sub(r"\[.+? : (.+?)\]", r"\1", text)
    return text

# Cargar el CSV
df = pd.read_csv("NLU-Data-Home-Domain-All.csv", delimiter=";")

print("Columnas del CSV:", df.columns)
print("Primeras filas:")
print(df.head(5))

# Verificar qué intenciones están disponibles
unique_intents = df['intent'].unique()
print(f"\nIntenciones únicas en el dataset: {len(unique_intents)}")
print("Primeras 20 intenciones:", unique_intents[:20])

# Filtrar solo las intenciones que tenemos mapeadas
mapped_intents = [intent for intent in unique_intents if intent in INTENT_MAP]
print(f"\nIntenciones que podemos mapear: {mapped_intents}")

translator = Translator()
results = {}
processed_count = 0
max_examples_per_intent = 15  # Limitar para no exceder límites de Google Translate

print("\nComenzando traducción...")

for _, row in df.iterrows():
    intent = row['intent']
    text = row['answer_annotation']
    scenario = row['scenario']
    
    # Solo procesar intenciones mapeadas y textos válidos
    if intent in INTENT_MAP and pd.notnull(text) and text != "null":
        intent_es = INTENT_MAP[intent]
        
        # Limitar ejemplos por intención
        if intent_es not in results:
            results[intent_es] = []
        
        if len(results[intent_es]) >= max_examples_per_intent:
            continue
        
        clean_text = remove_annotations(text)
        
        try:
            translated = translator.translate(clean_text, src='en', dest='es').text
            results[intent_es].append({
                "text_es": translated,
                "original_text": clean_text,
                "scenario": scenario,
                "original_intent": intent
            })
            
            processed_count += 1
            print(f"Procesado {processed_count}: {intent} -> {intent_es}: {clean_text[:50]}...")
            
            # Pausa para evitar rate limiting
            time.sleep(random.uniform(0.1, 0.3))
            
        except Exception as e:
            print(f"Error traduciendo: {clean_text} ({e})")
            continue

# Guardar resultados con estadísticas
output_data = {
    "translated_examples": results,
    "statistics": {
        "total_processed": processed_count,
        "intents_found": len(results),
        "examples_per_intent": {intent: len(examples) for intent, examples in results.items()},
        "available_intents_in_dataset": list(unique_intents),
        "mapped_intents": list(INTENT_MAP.keys())
    }
}

with open("tools/translated_examples_from_csv.json", "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Procesamiento completado!")
print(f"📊 Total ejemplos procesados: {processed_count}")
print(f"🎯 Intenciones con ejemplos:")
for intent, examples in results.items():
    print(f"  - {intent}: {len(examples)} ejemplos")

print(f"\n📄 Resultados guardados en: tools/translated_examples_from_csv.json")

# Mostrar algunos ejemplos traducidos
print("\n🔍 Ejemplos traducidos (muestra):")
for intent, examples in results.items():
    if examples:
        print(f"\n{intent.upper()}:")
        for i, example in enumerate(examples[:3]):
            print(f"  {i+1}. Original: {example['original_text']}")
            print(f"     Traducido: {example['text_es']}")