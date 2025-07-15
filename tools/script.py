import pandas as pd
import json

# Cargar los dos archivos
print("🔄 Cargando archivos .parquet...")
df_examples = pd.read_parquet('shopping_queries_dataset_examples.parquet')
df_products = pd.read_parquet('shopping_queries_dataset_products.parquet')

# Filtrar solo productos en español y versión pequeña
df_examples = df_examples[(df_examples['product_locale'] == 'es') & (df_examples['small_version'] == 1)]
df_products = df_products[df_products['product_locale'] == 'es']

# Hacer merge por product_id y product_locale para obtener product_title
df = pd.merge(df_examples, df_products, on=['product_locale', 'product_id'], how='left')

examples = []

# Intención: buscar_producto
mask_b = df['esci_label'].isin(['E', 'S'])
for _, row in df[mask_b].iterrows():
    query = row['query']
    title = row['product_title']
    if pd.notnull(title):
        text = f"Buscar '{query}' relacionado con '{title}'"
    else:
        text = query
    examples.append({"text": text, "intent": "buscar_producto"})

# Intención: comparar_precios
subs = df[df['esci_label'] == 'S']
for qid, group in subs.groupby('query_id'):
    titles = group['product_title'].dropna().unique()[:2]
    if len(titles) == 2:
        text = f"Comparar {titles[0]} y {titles[1]}"
        examples.append({"text": text, "intent": "comparar_precios"})

# Guardar en JSON
with open('intent_examples.json', 'w', encoding='utf-8') as f:
    json.dump({"examples": examples}, f, ensure_ascii=False, indent=2)

print("✅ JSON generado con", len(examples), "ejemplos")
