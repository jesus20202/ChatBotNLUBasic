class PromptBuilder:
    def build_context(self, intent: str, entities: dict, db_results: list) -> str:
        context = ""
        # Información general del usuario
        if intent == "buscar_producto":
            context += "El usuario está buscando productos"
            if "marca" in entities:
                context += f" de la marca {entities['marca']}"
            if "categoria" in entities:
                context += f" en la categoría {entities['categoria']}"
            if "rango_precio" in entities:
                rp = entities["rango_precio"]
                if "min" in rp and "max" in rp:
                    context += f" con precio entre {rp['min']} y {rp['max']}"
                elif "min" in rp:
                    context += f" con precio mayor a {rp['min']}"
                elif "max" in rp:
                    context += f" con precio menor a {rp['max']}"
            if "caracteristicas" in entities:
                context += f" con características: {', '.join(entities['caracteristicas'])}"
            context += ".\n"

        elif intent == "recomendar_categoria":
            context += "El usuario solicita recomendaciones"
            if "categoria" in entities:
                context += f" en la categoría {entities['categoria']}"
            context += ".\n"

        elif intent == "comparar_precios":
            context += "El usuario quiere comparar precios"
            if "marca" in entities:
                context += f" de la marca {entities['marca']}"
            if "categoria" in entities:
                context += f" en la categoría {entities['categoria']}"
            context += ".\n"

        elif intent == "info_producto":
            context += "El usuario solicita información detallada"
            if "marca" in entities:
                context += f" de la marca {entities['marca']}"
            if "categoria" in entities:
                context += f" en la categoría {entities['categoria']}"
            context += ".\n"

        # Formatear resultados de la BD
        if db_results:
            context += "Resultados encontrados:\n"
            for idx, prod in enumerate(db_results, 1):
                context += (
                    f"{idx}. {getattr(prod, 'nombre', '')}\n"
                    f"   Marca: {getattr(prod, 'marca', '')}\n"
                    f"   Precio: {getattr(prod, 'precio', '')}\n"
                    f"   Stock: {getattr(prod, 'stock', '')}\n"
                )
        else:
            context += "No se encontraron resultados en la base de datos.\n"

        # Prompt final para el LLM
        prompt = (
            f"{context}\n"
            "Responde de forma clara y útil para el usuario. Si no hay resultados, ofrece alternativas o ayuda."
        )
        return prompt