from .base_scraper import BaseScraper
import re
from urllib.parse import quote_plus

class MercadoLibreScraper(BaseScraper):
    def __init__(self):
        super().__init__(delay=2)  # MercadoLibre es estricto
        self.base_url = "https://listado.mercadolibre.com.pe"

    async def search_product(self, product_name: str, limit: int = 5) -> list:
        """Buscar producto en MercadoLibre"""
        query = quote_plus(product_name)
        search_url = f"{self.base_url}/{query}"

        soup = await self.safe_request(search_url)
        if not soup:
            return []

        products = []
        
        # Múltiples selectores para encontrar los productos
        product_cards = (
            soup.find_all('div', class_='ui-search-result__wrapper') or
            soup.find_all('li', class_='ui-search-layout__item') or
            soup.find_all('div', class_='ui-search-result') or
            soup.find_all('div', {'class': re.compile(r'ui-search.*result')})
        )

        for card in product_cards[:limit]:
            try:
                product_data = self.parse_product_card(card)
                if product_data:
                    products.append(product_data)
            except Exception as e:
                print(f"Error parseando producto: {e}")
                continue

        return products

    def parse_product_card(self, card) -> dict:
        """Parsear card de producto con múltiples selectores"""
        try:
            # Título - múltiples selectores
            title = self.extract_title(card)
            
            # Precio - múltiples selectores
            price = self.extract_price_from_card(card)
            
            # Link - múltiples selectores
            link = self.extract_link(card)
            
            # Imagen - múltiples selectores
            image = self.extract_image(card)
            
            # Vendedor - múltiples selectores
            seller = self.extract_seller(card)
            
            # Ubicación - múltiples selectores
            location = self.extract_location(card)
            
            # Envío gratis
            free_shipping = self.extract_shipping_info(card)
            
            # Rating/Reviews
            rating = self.extract_rating(card)

            return {
                'title': title,
                'price': price,
                'currency': 'PEN',
                'link': link,
                'image': image,
                'seller': seller,
                'location': location,
                'free_shipping': free_shipping,
                'rating': rating,
                'source': 'MercadoLibre',
                'available': True
            }

        except Exception as e:
            print(f"Error en parse_product_card: {e}")
            return None

    def extract_title(self, card) -> str:
        """Extraer título con múltiples selectores"""
        selectors = [
            'h2.ui-search-item__title',
            '.ui-search-item__title',
            'h2[class*="title"]',
            'a[class*="title"]',
            '.ui-search-item__title-label',
            'h2',
            'a[title]'
        ]
        
        for selector in selectors:
            element = card.select_one(selector)
            if element:
                title = element.get_text(strip=True) or element.get('title', '')
                if title and len(title) > 5:  # Validar que el título tenga contenido
                    return title
        
        return "Sin título"

    def extract_price_from_card(self, card) -> float:
        """Extraer precio con múltiples selectores"""
        selectors = [
            '.andes-money-amount__fraction',
            '.price-tag-fraction',
            '.andes-money-amount-combo__fraction',
            '.ui-search-price__second-line .andes-money-amount__fraction',
            '.ui-search-price .andes-money-amount__fraction',
            '[class*="price"] [class*="fraction"]',
            '.price-tag-amount',
            '.andes-money-amount'
        ]
        
        for selector in selectors:
            element = card.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                if price_text:
                    price = self.extract_price(price_text)
                    if price > 0:
                        return price
        
        return 0.0

    def extract_link(self, card) -> str:
        """Extraer link con múltiples selectores"""
        selectors = [
            'a.ui-search-link',
            'a.ui-search-item__group__element',
            'a[href*="MLU"]',
            'a[href*="MLA"]',
            'a[href*="articulo"]',
            'h2 a',
            'a[href*="mercadolibre"]'
        ]
        
        for selector in selectors:
            element = card.select_one(selector)
            if element and element.get('href'):
                href = element['href']
                # Asegurar URL completa
                if href.startswith('/'):
                    href = f"https://mercadolibre.com.pe{href}"
                elif not href.startswith('http'):
                    href = f"https://{href}"
                return href
        
        return ""

    def extract_image(self, card) -> str:
        """Extraer imagen con múltiples selectores"""
        selectors = [
            'img.ui-search-result-image__element',
            '.ui-search-result-image img',
            'img[src*="http"]',
            'img[data-src*="http"]',
            'img.lazy',
            'img'
        ]
        
        for selector in selectors:
            element = card.select_one(selector)
            if element:
                # Intentar src primero, luego data-src
                src = element.get('src') or element.get('data-src') or element.get('data-lazy')
                if src and ('http' in src or src.startswith('//')):
                    return src.replace('//', 'https://') if src.startswith('//') else src
        
        return ""

    def extract_seller(self, card) -> str:
        """Extraer vendedor con múltiples selectores"""
        selectors = [
            '.ui-search-item__brand-discoverability',
            '.ui-search-item__brand',
            '[class*="brand"]',
            '[class*="seller"]',
            '.ui-search-item__group__element .ui-search-item__brand-discoverability',
            '.seller-info'
        ]
        
        for selector in selectors:
            element = card.select_one(selector)
            if element:
                seller = element.get_text(strip=True)
                if seller and seller.lower() not in ['', 'por']:
                    return seller
        
        return "Sin vendedor"

    def extract_location(self, card) -> str:
        """Extraer ubicación con múltiples selectores"""
        selectors = [
            '.ui-search-item__location',
            '.ui-search-item__location-label',
            '[class*="location"]',
            '.ui-search-item__group__element .ui-search-item__location'
        ]
        
        for selector in selectors:
            element = card.select_one(selector)
            if element:
                location = element.get_text(strip=True)
                if location:
                    return location
        
        return ""

    def extract_shipping_info(self, card) -> bool:
        """Extraer información de envío gratis"""
        selectors = [
            '.ui-search-item__shipping',
            '[class*="shipping"]',
            '.ui-search-item__group__element .ui-search-item__shipping'
        ]
        
        for selector in selectors:
            element = card.select_one(selector)
            if element:
                shipping_text = element.get_text(strip=True).lower()
                if 'gratis' in shipping_text or 'free' in shipping_text:
                    return True
        
        return False

    def extract_rating(self, card) -> float:
        """Extraer rating/calificación"""
        selectors = [
            '.ui-search-reviews__rating',
            '[class*="rating"]',
            '.ui-search-item__reviews-rating'
        ]
        
        for selector in selectors:
            element = card.select_one(selector)
            if element:
                rating_text = element.get_text(strip=True)
                # Buscar números decimales como 4.5, 4,5, etc.
                rating_match = re.search(r'(\d+[.,]\d+|\d+)', rating_text)
                if rating_match:
                    try:
                        return float(rating_match.group(1).replace(',', '.'))
                    except:
                        continue
        
        return 0.0

    def extract_price(self, price_text: str) -> float:
        """Extraer precio numérico mejorado"""
        if not price_text:
            return 0.0
        
        # Limpiar el texto del precio
        price_clean = re.sub(r'[^\d.,]', '', price_text)
        
        # Manejar diferentes formatos de número
        if ',' in price_clean and '.' in price_clean:
            # Formato como 1,234.56
            if price_clean.rindex(',') < price_clean.rindex('.'):
                price_clean = price_clean.replace(',', '')
            # Formato como 1.234,56
            else:
                price_clean = price_clean.replace('.', '').replace(',', '.')
        elif ',' in price_clean:
            # Si solo hay coma, podría ser separador decimal (europeo) o miles
            parts = price_clean.split(',')
            if len(parts) == 2 and len(parts[1]) <= 2:
                # Probablemente separador decimal
                price_clean = price_clean.replace(',', '.')
            else:
                # Probablemente separador de miles
                price_clean = price_clean.replace(',', '')
        
        try:
            return float(price_clean)
        except:
            return 0.0