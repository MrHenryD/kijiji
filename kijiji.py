import time
from typing import List, Union
from dataclasses import dataclass

import click
import requests
from bs4 import BeautifulSoup


@dataclass
class Product:
    title: str
    description: str
    img: str
    url: str
    price: Union[str, float]
    price_is_decimal: bool
        
    def __str__(self):
        return f"{self.title} - {self.price} @ {self.url}"
    
    def __repr__(self):
        return self.__str__()
    
class Kijiji:    
    DOMAIN = "https://www.kijiji.com"
    SEARCH_API = "https://www.kijiji.ca/b-search.html"
    DELAY = 5
    HEADERS = {
        'authority': 'www.kijiji.ca',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.kijiji.ca/',
        'accept-language': 'en-US,en;q=0.9',
    }
    
    def _search(self, search_term: str, max_price: float, min_price: float,
                page_index: int,                
               ) -> requests.Response:
        
        params = (
            ('formSubmit', 'true'),
            ('rb', 'true'),
            ('adIdRemoved', ''),
            ('adPriceType', ''),
            ('brand', ''),
            ('carproofOnly', 'false'),
            ('categoryName', ''),
            ('cpoOnly', 'false'),
            ('gpTopAd', 'false'),
            ('highlightOnly', 'false'),
            ('locationId', '9004'),
            ('minPrice', str(min_price)),
            ('maxPrice', str(max_price)),
            ('origin', ''),
            ('pageNumber', str(page_index)),
            ('searchView', 'LIST'),
            ('sortByName', 'dateDesc'),
            ('userId', ''),
            ('urgentOnly', 'false'),
            ('keywords', str(search_term)),
            ('categoryId', '0'),
            ('dc', 'true'),
        )
        response = requests.get(self.SEARCH_API, headers=self.HEADERS, params=params)
        return response
    
    def get(self, search_term: str, max_price: float, min_price: float,
            num_pages: int = 5,
           ) -> List[Product]:
        products = []
        for page_index in range(1, num_pages + 1):
            print(f"Time delay: {self.DELAY}s...")
            time.sleep(self.DELAY)
            print(f"Searching on {search_term}. Page index {page_index}...")            
            response = self._search(search_term=search_term, page_index=page_index,
                                    min_price=min_price, max_price=max_price,
                                   )
            if response:
                soup = BeautifulSoup(response.content, features="lxml")
                searches = soup.find_all("div", {"class": "search-item"})                
                if searches:
                    for search in searches:
                        try:
                            title = search.find("a", {"class": "title"}).text.strip()
                            description = search.find("div", {"class": "description"}).text.strip()
                            img = search.find("img", {}).get("src")
                            url = self.DOMAIN + search.find("a", {"class": "title"}).get("href")
                            price_is_decimal = search.find("div", {"class": "price"}).text.strip().replace("$", "").isdecimal()
                            
                            if price_is_decimal:
                                price = float(search.find("div", {"class": "price"}).text.strip().replace("$", ""))
                            else:
                                price = search.find("div", {"class": "price"}).text.strip().replace("$", "")
                            
                            product = Product(
                                    title,
                                    description,
                                    img,
                                    url,
                                    price,
                                    price_is_decimal,
                                )                            
                            products.append(product)
                            print(product, "\n")

                        except Exception as e:
                            print(e)
                            continue
                else:
                    break
            else:
                break
        
        return products

@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.option('--search', help='search term')
@click.option('--min_price', help='Maximum price')
@click.option('--max_price', help='Minimum price')
@click.option('--pages', help='number of pages (default 3)')
def main(search: str, min_price: float, max_price: float, pages: int = 3):
    
    print(f"""
    --- KIJIJI API ---
    Search: {search}
    Min Price: {min_price}
    Max Price: {max_price}
    Pages: {pages}
    """)

    kijiji = Kijiji()
    products = kijiji.get(search_term=str(search), 
                          num_pages=int(pages), 
                          min_price=float(min_price), 
                          max_price=float(max_price),
                          )
    return products

if __name__ == "__main__":
    main()

