from abc import ABC, abstractmethod
import aiohttp
from bs4 import BeautifulSoup
import asyncio
from fake_useragent import UserAgent
import logging

class BaseScraper(ABC):
    def __init__(self, delay=1):
        self.ua = UserAgent()
        self.delay = delay
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            headers={'User-Agent': self.ua.random}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @abstractmethod
    async def search_product(self, product_name: str, limit: int = 5) -> list:
        pass

    @abstractmethod
    def parse_product_card(self, element) -> dict:
        pass

    async def safe_request(self, url: str) -> BeautifulSoup:
        """Request con manejo de errores"""
        try:
            await asyncio.sleep(self.delay)  # Rate limiting
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    return BeautifulSoup(html, 'lxml')
                else:
                    logging.warning(f"Status {response.status} for {url}")
                    return None
        except Exception as e:
            logging.error(f"Error scraping {url}: {e}")
            return None