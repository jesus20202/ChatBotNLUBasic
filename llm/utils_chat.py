def extract_product_name(message: str, entities: dict) -> str:
    """Extraer nombre del producto para scraping"""
    name_parts = []
    
    # Si marca existe y es string, usarla
    if "marca" in entities and isinstance(entities["marca"], str) and entities["marca"].strip():
        name_parts.append(entities["marca"])
    
    # Para categoría, verificar si es ID o nombre
    if "categoria" in entities:
        if isinstance(entities["categoria"], str) and entities["categoria"].strip():
            name_parts.append(entities["categoria"])
        elif isinstance(entities["categoria"], int):
            try:
                from database.connection import get_db
                from models.database import Categoria
                db = next(get_db())
                categoria_obj = db.query(Categoria).filter(Categoria.id == entities["categoria"]).first()
                if categoria_obj:
                    name_parts.append(categoria_obj.nombre)
            except Exception:
                pass
    
    # Si no hay entidades útiles, usar mensaje completo
    if not name_parts:
        return message.strip()
    
    return " ".join(name_parts)