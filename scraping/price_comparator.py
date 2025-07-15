import asyncio
from typing import List, Dict
from .mercadolibre_scraper import MercadoLibreScraper
from .falabella_scraper import FalabellaScraper
import logging

class PriceComparator:
    def __init__(self):
        self.scrapers = {
            'mercadolibre': MercadoLibreScraper(),
            'falabella': FalabellaScraper()
        }

    async def compare_prices(self, product_name: str, db_price: float = None) -> dict:
        """Comparar precios en múltiples sitios"""
        logging.info(f"🔍 Comparando precios para: {product_name}")

        all_results = {}

        # Scraping paralelo
        tasks = []
        for site_name, scraper in self.scrapers.items():
            task = self.scrape_site(site_name, scraper, product_name)
            tasks.append(task)

        # Ejecutar todos en paralelo
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Procesar resultados
        for i, result in enumerate(results):
            site_name = list(self.scrapers.keys())[i]
            if isinstance(result, Exception):
                logging.error(f"❌ Error en {site_name}: {result}")
                all_results[site_name] = []
            else:
                all_results[site_name] = result

        # Análisis de precios
        analysis = self.analyze_prices(all_results, db_price)

        return {
            'query': product_name,
            'db_price': db_price,
            'results': all_results,
            'analysis': analysis,
            'timestamp': asyncio.get_event_loop().time()
        }

    async def scrape_site(self, site_name: str, scraper, product_name: str) -> list:
        """Scraping individual por sitio"""
        try:
            async with scraper as s:
                return await s.search_product(product_name, limit=3)
        except Exception as e:
            logging.error(f"Error scraping {site_name}: {e}")
            return []

    def analyze_prices(self, results: dict, db_price: float = None) -> dict:
        """Analizar precios encontrados"""
        all_prices = []

        # Recopilar todos los precios
        for site, products in results.items():
            for product in products:
                if product['price'] > 0:
                    all_prices.append({
                        'price': product['price'],
                        'site': site,
                        'title': product['title'],
                        'link': product['link']
                    })

        if not all_prices:
            return {'status': 'no_results'}

        # Ordenar por precio
        all_prices.sort(key=lambda x: x['price'])

        # Análisis
        min_price = all_prices[0]['price']
        max_price = all_prices[-1]['price']
        avg_price = sum(p['price'] for p in all_prices) / len(all_prices)

        analysis = {
            'status': 'success',
            'total_found': len(all_prices),
            'min_price': min_price,
            'max_price': max_price,
            'avg_price': avg_price,
            'best_deal': all_prices[0],
            'price_range': max_price - min_price
        }

        # Comparar con precio de BD si existe
        if db_price is not None:
            analysis['db_comparison'] = {
                'db_price': db_price,
                'savings_vs_min': max(0, db_price - min_price),
                'savings_vs_avg': max(0, db_price - avg_price),
                'db_is_competitive': db_price <= avg_price
            }

        return analysis