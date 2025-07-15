from .base_scraper import BaseScraper
import re
from urllib.parse import quote_plus
import json

class FalabellaScraper(BaseScraper):
    def __init__(self):
        super().__init__(delay=1.5)
        self.base_url = "https://www.falabella.com.pe"

    async def search_product(self, product_name: str, limit: int = 5) -> list:
        """Buscar producto en Falabella"""
        query = quote_plus(product_name)
        search_url = f"{self.base_url}/falabella-pe/search?Ntt={query}"

        soup = await self.safe_request(search_url)
        if not soup:
            return []

        products = []
        
        # Múltiples selectores para Falabella
        product_cards = self.find_product_cards(soup)
        
        # Si no encuentra productos, intentar con datos JSON embebidos
        if not product_cards:
            products = self.extract_from_json_data(soup)
            return products[:limit]

        for card in product_cards[:limit]:
            try:
                product_data = self.parse_product_card(card)
                if product_data:
                    products.append(product_data)
            except Exception as e:
                print(f"Error parseando producto Falabella: {e}")
                continue

        return products

    def find_product_cards(self, soup):
        """Buscar cards de productos con selectores específicos de Falabella"""
        selectors = [
            'div.pod-summary',  # Selector principal de Falabella
            'div.jsx-2858414180.jsx-3390574944.pod-summary',
            'div[class*="pod-summary"]',
            'div.jsx-2858414180',
            'div[class*="pod-summary-4_GRID"]'
        ]
        
        for selector in selectors:
            cards = soup.select(selector)
            if cards:
                # Filtrar cards que son anuncios patrocinados
                filtered_cards = []
                for card in cards:
                    # Verificar si tiene el elemento "Patrocinado"
                    sponsored = card.select_one('.patrocinado-pod .patrocinado-title')
                    if not sponsored:
                        filtered_cards.append(card)
                
                if filtered_cards:
                    print(f"Encontrados {len(filtered_cards)} productos NO patrocinados con selector: {selector}")
                    return filtered_cards
                else:
                    print(f"Encontrados {len(cards)} productos (todos patrocinados) con selector: {selector}")
                    return cards  # Devolver todos si no hay no-patrocinados
        
        return []

    def extract_from_json_data(self, soup):
        """Extraer productos de datos JSON embebidos"""
        products = []
        
        # Buscar scripts con datos JSON
        scripts = soup.find_all('script', type='application/ld+json') + \
                 soup.find_all('script', type='application/json')
        
        for script in scripts:
            try:
                if script.string:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and 'products' in data:
                        for product in data['products']:
                            products.append(self.parse_json_product(product))
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and '@type' in item and 'Product' in item['@type']:
                                products.append(self.parse_json_product(item))
            except:
                continue
        
        return products

    def parse_json_product(self, product_data):
        """Parsear producto desde datos JSON"""
        try:
            return {
                'title': product_data.get('name', 'Sin título'),
                'price': float(product_data.get('offers', {}).get('price', 0)),
                'currency': 'PEN',
                'link': product_data.get('url', ''),
                'image': product_data.get('image', ''),
                'seller': 'Falabella',
                'location': 'Perú',
                'source': 'Falabella',
                'available': True
            }
        except:
            return None

    def parse_product_card(self, card) -> dict:
        """Parsear card de producto Falabella con múltiples selectores"""
        try:
            # Título - múltiples selectores
            title = self.extract_title(card)
            
            # Precio - múltiples selectores
            price = self.extract_price_from_card(card)
            
            # Link - múltiples selectores
            link = self.extract_link(card)
            
            # Imagen - múltiples selectores
            image = self.extract_image(card)
            
            # Descuento
            discount = self.extract_discount(card)
            
            # Rating
            rating = self.extract_rating(card)
            
            # Marca
            brand = self.extract_brand(card)

            return {
                'title': title,
                'price': price,
                'currency': 'PEN',
                'link': link,
                'image': image,
                'seller': 'Falabella',
                'brand': brand,
                'location': 'Perú',
                'discount': discount,
                'rating': rating,
                'source': 'Falabella',
                'available': True
            }

        except Exception as e:
            print(f"Error en parse_product_card Falabella: {e}")
            return None

    def extract_title(self, card) -> str:
        """Extraer título con selectores específicos de Falabella"""
        selectors = [
            'b.pod-subTitle',  # Selector específico de Falabella
            'b[class*="subTitle"]',
            'b[id*="pod-displaySubTitle"]',
            'b.jsx-2858414180.copy2.primary',
            '[class*="pod-subTitle"]',
            '[class*="subTitle"]'
        ]
        
        # Palabras a filtrar que no son títulos válidos
        invalid_titles = ['patrocinado', 'sponsored', 'ad', 'publicidad', 'promo']
        
        for selector in selectors:
            element = card.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and len(title) > 3:
                    # Verificar que no sea un título inválido
                    if title.lower() not in invalid_titles:
                        return title
        
        return "Sin título"

    def extract_price_from_card(self, card) -> float:
        """Extraer precio con selectores específicos de Falabella"""
        selectors = [
            'span.copy10.primary.medium',  # Precio actual específico
            'li[data-internet-price] span.copy10',
            'li.prices-0 span.copy10',
            'ol.pod-prices span.copy10',
            '[data-internet-price] span',
            'span.copy10',
            '.prices-0 span',
            'li.prices-0 span.jsx-233704000',
            'span[class*="copy10"]'
        ]
        
        for selector in selectors:
            element = card.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                if price_text and 'S/' in price_text:
                    price = self.extract_price(price_text)
                    if price > 0:
                        return price
        
        # Fallback: buscar en data-internet-price
        price_element = card.select_one('li[data-internet-price]')
        if price_element:
            price_data = price_element.get('data-internet-price')
            if price_data:
                price = self.extract_price(price_data)
                if price > 0:
                    return price
        
        return 0.0

    def extract_link(self, card) -> str:
        """Extraer link con múltiples selectores"""
        selectors = [
            'a[href*="/p/"]',
            'a.pod-summary-title',
            'a[href*="product"]',
            'a[href*="falabella"]',
            'a[href*="MLU"]',  # Códigos de producto
            'a[href*="MLM"]',
            'a[href*="MLA"]',
            'h2 a[href]',
            'h3 a[href]',
            '.product-title a[href]',
            '.pod-summary-title a[href]',
            'a[href]:not([href*="javascript"]):not([href="#"])'
        ]
        
        for selector in selectors:
            element = card.select_one(selector)
            if element and element.get('href'):
                href = element['href']
                # Filtrar enlaces que no son de productos
                if any(skip in href for skip in ['javascript:', '#', 'mailto:', 'tel:']):
                    continue
                
                # Manejar URLs relativas
                if href.startswith('/'):
                    return f"{self.base_url}{href}"
                elif href.startswith('http'):
                    return href
                elif href and not href.startswith('http'):
                    return f"{self.base_url}/{href}"
        
        return ""

    def extract_image(self, card) -> str:
        """Extraer imagen con múltiples selectores"""
        selectors = [
            'img[src*="falabella"]',
            'img[data-src*="falabella"]',
            'img[src*="http"]',
            'img[data-src*="http"]',
            'img.lazy',
            'img[data-lazy*="http"]',
            'img'
        ]
        
        for selector in selectors:
            element = card.select_one(selector)
            if element:
                src = (element.get('src') or 
                      element.get('data-src') or 
                      element.get('data-lazy') or 
                      element.get('data-original'))
                
                if src:
                    # Manejar URLs relativas y protocolos
                    if src.startswith('//'):
                        return f"https:{src}"
                    elif src.startswith('/'):
                        return f"{self.base_url}{src}"
                    elif src.startswith('http'):
                        return src
        
        return ""

    def extract_discount(self, card) -> int:
        """Extraer porcentaje de descuento con selectores específicos"""
        selectors = [
            'span.discount-badge-item',  # Selector específico de Falabella
            'span[id*="Pod-badges--"]',
            'span.jsx-3475638340',
            '.discount-badge span',
            'span[class*="discount-badge"]'
        ]
        
        for selector in selectors:
            element = card.select_one(selector)
            if element:
                discount_text = element.get_text(strip=True)
                # Buscar porcentaje en formato -29%
                discount_match = re.search(r'-?(\d+)%', discount_text)
                if discount_match:
                    return int(discount_match.group(1))
        
        return 0

    def extract_rating(self, card) -> float:
        """Extraer calificación con selectores específicos"""
        selectors = [
            'div[data-rating]',  # Selector específico de Falabella
            'div.jsx-1982392636.ratings',
            'div[id*="Pod-Rating"]',
            '.pod-rating',
            'div.ratings--container'
        ]
        
        for selector in selectors:
            element = card.select_one(selector)
            if element:
                # Intentar obtener rating del atributo data-rating
                rating_data = element.get('data-rating')
                if rating_data:
                    try:
                        return float(rating_data)
                    except:
                        continue
                
                # Contar estrellas llenas
                stars_filled = element.select('i.csicon-star_full_filled')
                if stars_filled:
                    return float(len(stars_filled))
        
        return 0.0

    def extract_brand(self, card) -> str:
        """Extraer marca del producto"""
        selectors = [
            '.brand',
            '.product-brand',
            '[class*="brand"]',
            '[data-brand]'
        ]
        
        # Filtrar valores que no son marcas válidas
        invalid_brands = ['(1)', '(2)', '(3)', '(4)', '(5)', '', 'patrocinado', 'sponsored']
        
        for selector in selectors:
            element = card.select_one(selector)
            if element:
                brand = element.get_text(strip=True) or element.get('data-brand', '')
                if brand and brand not in invalid_brands:
                    return brand
        
        return ""

    def extract_price(self, price_text: str) -> float:
        """Extraer precio numérico mejorado para Falabella"""
        if not price_text:
            return 0.0
        
        # Remover texto común de Falabella
        price_text = re.sub(r'(S/\.?|PEN|soles?|antes|ahora|precio|normal)', '', price_text, flags=re.IGNORECASE)
        
        # Limpiar el texto del precio
        price_clean = re.sub(r'[^\d.,]', '', price_text)
        
        if not price_clean:
            return 0.0
        
        # Manejar diferentes formatos de número
        if ',' in price_clean and '.' in price_clean:
            # Formato como 1,234.56
            if price_clean.rindex(',') < price_clean.rindex('.'):
                price_clean = price_clean.replace(',', '')
            # Formato como 1.234,56
            else:
                price_clean = price_clean.replace('.', '').replace(',', '.')
        elif ',' in price_clean:
            # Si solo hay coma, determinar si es decimal o separador de miles
            comma_pos = price_clean.rfind(',')
            if len(price_clean) - comma_pos - 1 <= 2:
                # Probablemente decimal
                price_clean = price_clean.replace(',', '.')
            else:
                # Probablemente separador de miles
                price_clean = price_clean.replace(',', '')
        
        try:
            return float(price_clean)
        except:
            return 0.0