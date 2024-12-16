import requests
from bs4 import BeautifulSoup as BS

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.52',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
}


def get_data(html):
    soup = BS(html, "html.parser")
    items = soup.find_all("li", class_="results-item-wrap", limit=5)
    kino = []
    for i in items:
        kino.append({
            "url": f"https://w140.zona.plus{i.find('a').get('href')}",
        })
    return kino


def parse_movies():
    url = "https://w140.zona.plus/movies/filter/rating-8"
    html = requests.get(url=url, headers=HEADERS)
    data = get_data(html.text)
    return data


def get_search_data(html):
    soup = BS(html, "html.parser")
    items = soup.find_all("li", class_="results-item-wrap", limit=3)
    kino = []
    for i in items:
        kino.append({
            "url": f"https://w140.zona.plus{i.find('a').get('href')}",
        })
    return kino

def search_movie_by_name(movie_name: str):
    """Ищет фильмы по названию и возвращает список найденных фильмов."""
    search_url = f"https://w140.zona.plus/search/{movie_name}"  # URL для поиска фильмов
    html = requests.get(url=search_url, headers=HEADERS)
    data = get_search_data(html.text)
    return data

def get_search_data_by_code(html):
    soup = BS(html, "html.parser")
    items = soup.find_all("li", class_="results-item-wrap", limit=1)
    kino = []
    for i in items:
        kino.append({
            "url": f"https://w140.zona.plus{i.find('a').get('href')}",
        })
    return kino


def search_movie_by_code(movie_name: str):
    """Ищет фильмы по названию и возвращает список найденных фильмов."""
    search_url = f"https://w140.zona.plus/search/{movie_name}"  # URL для поиска фильмов
    html = requests.get(url=search_url, headers=HEADERS)
    data = get_search_data_by_code(html.text)
    return data