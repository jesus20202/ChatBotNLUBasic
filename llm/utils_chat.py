def extract_product_name(message: str, entities: dict) -> str:
    if "marca" in entities and "categoria" in entities:
        return f"{entities['marca']} {entities['categoria']}"
    if "marca" in entities:
        return entities["marca"]
    if "categoria" in entities:
        return entities["categoria"]
    return message

def build_enriched_context(nlu_result, db_products, comparison):
    context = f"Intención detectada: {nlu_result['intent']}\n"
    if db_products:
        prod = db_products[0]
        context += f"En tu tienda tienes el producto '{prod.nombre}' a S/. {prod.precio}.\n"
    if comparison and comparison['analysis']['status'] == 'success':
        best = comparison['analysis']['best_deal']
        context += (
            f"En MercadoLibre/Falabella encontré '{best['title']}' a S/. {best['price']}.\n"
            f"Puedes ahorrar S/. {comparison['analysis']['db_comparison']['savings_vs_min']:.2f} si compras fuera.\n"
        )
    else:
        context += "No se encontraron mejores precios en otras tiendas.\n"
    context += "¿Te interesa ver más detalles?"
    return context

def build_basic_context(nlu_result, db_products):
    context = f"Intención detectada: {nlu_result['intent']}\n"
    if db_products:
        context += "Resultados encontrados:\n"
        for idx, prod in enumerate(db_products, 1):
            context += (
                f"{idx}. {prod.nombre}\n"
                f"   Marca: {prod.marca}\n"
                f"   Precio: {prod.precio}\n"
                f"   Stock: {prod.stock}\n"
            )
    else:
        context += "No se encontraron resultados en la base de datos.\n"
    return context