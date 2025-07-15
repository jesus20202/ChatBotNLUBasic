def extract_product_name(message: str, entities: dict) -> str:
    if "marca" in entities and "categoria" in entities:
        return f"{entities['marca']} {entities['categoria']}"
    if "marca" in entities:
        return entities["marca"]
    if "categoria" in entities:
        return entities["categoria"]
    return message

