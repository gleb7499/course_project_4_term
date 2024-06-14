from bs4 import BeautifulSoup
import asyncio
import aiohttp


class Elem:
    """Класс для хранения спарсенных данных с одной страницы."""

    def __init__(self):
        self.names = []
        self.prices = []
        self.page = []


class Parsing:
    """Класс для асинхронного парсинга данных с нескольких страниц."""

    def __init__(self):
        self.data = []
        self.total = 0

    async def _get_page_data(self, session, page):
        """Асинхронно получает данные с одной страницы."""
        el = Elem()
        try:
            async with session.get(f"https://shop.mts.by/phones/?page={page}") as response:
                soup = BeautifulSoup(await response.text(), "lxml")
                el.names.extend(name.text for name in soup.findAll(class_="linkTovar"))
                el.prices.extend(price.text for price in soup.select(".products__unit__body.products__unit__body--hover .products__unit__price__number.products__unit__price__number--full"))
                el.page.append(page)
                self.data.append(el)
        except Exception as e:
            raise Exception(f"Произошла ошибка при получении данных со страницы {page}") from None

    async def _get_gather(self):
        """Асинхронно получает данные со всех страниц."""
        tasks = []
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get('https://shop.mts.by/phones/')
                soup = BeautifulSoup(await response.text(), "lxml")
                pages_count = int(soup.findAll(class_="pagination__unit")[-1].text.strip())
                self.total = int(soup.findAll(class_="products-filters__result__title")[0].text.split()[1])
                for page in range(1, pages_count + 1):
                    tasks.append(asyncio.create_task(self._get_page_data(session, page)))
                await asyncio.gather(*tasks)
        except Exception as e:
            raise e

    def do_parsing(self):
        """Запускает процесс парсинга."""
        try:
            asyncio.run(self._get_gather())
        except Exception as e:
            raise e
