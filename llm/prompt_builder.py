class PromptBuilder:
    def build_context(self, intent: str, entities: dict, db_results: list, comparison: dict = None) -> str:
        """
        Construye el contexto específico para cada intención
        """
        context = ""
        
        # Contexto específico por intención
        if intent == "buscar_producto":
            context += "El usuario está buscando productos"
            if "marca" in entities:
                context += f" de la marca {entities['marca']}"
            if "categoria" in entities:
                context += f" en la categoría {entities['categoria']}"
            if "rango_precio" in entities:
                rp = entities["rango_precio"]
                if "min" in rp and "max" in rp:
                    context += f" con precio entre S/. {rp['min']} y S/. {rp['max']}"
                elif "min" in rp:
                    context += f" con precio mayor a S/. {rp['min']}"
                elif "max" in rp:
                    context += f" con precio menor a S/. {rp['max']}"
            if "caracteristicas" in entities:
                context += f" con características: {', '.join(entities['caracteristicas'])}"
            context += ".\n"

        elif intent == "recomendar_categoria":
            context += "El usuario solicita recomendaciones"
            if "categoria" in entities:
                context += f" en la categoría {entities['categoria']}"
            context += ". Sugiere los mejores productos disponibles.\n"

        elif intent == "comparar_precios":
            context += "El usuario quiere comparar precios entre productos similares"
            if "marca" in entities:
                context += f" de la marca {entities['marca']}"
            if "categoria" in entities:
                context += f" en la categoría {entities['categoria']}"
            context += ". Muestra opciones ordenadas por precio.\n"

        elif intent == "comparar_precios_web":
            context += "El usuario quiere comparar precios en tiendas online como MercadoLibre o Falabella"
            if "marca" in entities:
                context += f" de la marca {entities['marca']}"
            if "categoria" in entities:
                context += f" en la categoría {entities['categoria']}"
            context += ".\n"

        elif intent == "info_producto":
            context += "El usuario solicita información detallada sobre productos"
            if "marca" in entities:
                context += f" de la marca {entities['marca']}"
            if "categoria" in entities:
                context += f" en la categoría {entities['categoria']}"
            context += ". Proporciona especificaciones técnicas y características.\n"

        elif intent == "saludo":
            context += "El usuario está saludando. Responde de forma amigable y pregunta cómo puedes ayudar.\n"

        elif intent == "ayuda":
            context += "El usuario solicita ayuda. Explica qué funciones están disponibles y cómo usar la plataforma.\n"

        else:
            context += f"El usuario tiene la intención '{intent}'. Responde de forma útil.\n"

        # Agregar información de comparación web si existe
        if intent == "comparar_precios_web" and comparison:
            if comparison.get('analysis', {}).get('status') == 'success':
                best = comparison['analysis']['best_deal']
                context += f"En tiendas online encontré '{best['title']}' a S/. {best['price']}.\n"
                if comparison['analysis']['db_comparison'].get('savings_vs_min'):
                    savings = comparison['analysis']['db_comparison']['savings_vs_min']
                    context += f"Puedes ahorrar S/. {savings:.2f} comprando online.\n"
            else:
                context += "No se encontraron mejores precios en tiendas online en este momento.\n"

        # Formatear resultados de la BD
        if db_results:
            context += f"\nProductos disponibles en nuestra tienda ({len(db_results)} resultados):\n"
            for idx, prod in enumerate(db_results[:10], 1):  # Limitar a 10 resultados
                context += (
                    f"{idx}. {getattr(prod, 'nombre', 'Sin nombre')}\n"
                    f"   Marca: {getattr(prod, 'marca', 'N/A')}\n"
                    f"   Precio: S/. {getattr(prod, 'precio', '0')}\n"
                    f"   Stock: {getattr(prod, 'stock', 0)} unidades\n"
                )
            if len(db_results) > 10:
                context += f"... y {len(db_results) - 10} productos más.\n"
        else:
            context += "\nNo se encontraron productos que coincidan con tu búsqueda en nuestra tienda.\n"

        # Prompt final específico por intención
        if intent == "buscar_producto":
            instruction = (
                "Presenta los productos de forma clara y atractiva. "
                "Si no hay resultados, sugiere alternativas o categorías similares."
            )
        elif intent == "recomendar_categoria":
            instruction = (
                "Recomienda los mejores productos destacando sus ventajas. "
                "Organiza por calidad-precio y popularidad."
            )
        elif intent == "comparar_precios":
            instruction = (
                "Compara los productos mostrando diferencias de precio y características. "
                "Ayuda al usuario a tomar la mejor decisión."
            )
        elif intent == "comparar_precios_web":
            instruction = (
                "Informa sobre precios online y compara con nuestra tienda. "
                "Menciona ventajas de comprar con nosotros (garantía, servicio, etc.)."
            )
        elif intent == "info_producto":
            instruction = (
                "Proporciona información detallada y técnica. "
                "Incluye especificaciones, garantía y recomendaciones de uso."
            )
        elif intent == "saludo":
            instruction = (
                "Saluda de forma amigable y profesional. "
                "Pregunta cómo puedes ayudar y menciona brevemente los servicios disponibles."
            )
        elif intent == "ayuda":
            instruction = (
                "Explica claramente cómo usar la plataforma. "
                "Menciona que pueden buscar productos, comparar precios, y solicitar recomendaciones."
            )
        else:
            instruction = "Responde de forma útil y profesional."

        prompt = f"{context}\n{instruction}\n\nRespuesta:"
        return prompt

    def build_fallback_prompt(self, message: str, intent: str = None, confidence: float = 0.0) -> str:
        """
        Construye un prompt para casos de fallback (baja confianza o sin entidades)
        """
        context = f"El usuario escribió: '{message}'\n"
        
        if intent:
            context += f"Intención detectada: {intent} (confianza: {confidence:.2f})\n"
        
        context += (
            "No se pudo procesar completamente la solicitud. "
            "Responde de forma útil sugiriendo cómo el usuario puede reformular su consulta "
            "o qué opciones están disponibles.\n"
        )
        
        instruction = (
            "Sé amigable y útil. Sugiere ejemplos de búsquedas como:\n"
            "- 'Busco laptops Lenovo baratas'\n"
            "- 'Recomiéndame celulares Samsung'\n"
            "- '¿Cuál es el precio en MercadoLibre?'\n"
            "- 'Compara precios de tablets'"
        )
        
        return f"{context}\n{instruction}\n\nRespuesta:"