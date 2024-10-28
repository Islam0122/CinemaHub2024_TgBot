import requests
from bs4 import BeautifulSoup as BS
from urllib.parse import quote

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.52',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
}


# def get_data(html, limit: int = 5):
#     soup = BS(html, "html.parser")
#     items = soup.find_all("article", class_="cat-item", limit=limit)  # Изменить limit по необходимости
#     kino = []
#
#     for i in items:
#         link = i.find('a', class_='link-title').get('href', '')  # Берём ссылку на фильм
#
#         kino.append({
#             "url": link
#         })
#
#     return kino
def get_data(html, limit: int = 5):
    soup = BS(html, "html.parser")
    items = soup.find_all("div", class_="col-sm-30 col-md-15 col-lg-15 margin_b20", limit=limit)  # Limit the number of items based on the parameter
    kino = []

    for i in items:
        link = i.find('a').get('href', '')  # Get the link to the movie

        title = i.find('h5').get_text(strip=True)  # Extract the title text, stripping whitespace

        if link:  # Ensure that the link is not empty
            kino.append({
                "title": title,
                "url": f"https://engvideo.net/{link}"
            })

    return kino


def parse_movies():
    url = "https://engvideo.net/ru/films/"

    try:
        html = requests.get(url, headers=HEADERS)
        html.raise_for_status()  # Проверка на ошибки

        return get_data(html.text, 5)

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []


def search_movie_by_name(movie_name: str):
    url = f"https://engvideo.net/ru/films/?title={movie_name}"
    html = requests.get(url=url, headers=HEADERS)

    if html.status_code == 200:
        data = get_data(html.text, 3)
        return data
    else:
        print(f"Error: {html.status_code}")
        return []


def search_movie_by_code(movie_name: str):
    """Ищет фильмы по названию и возвращает список найденных фильмов."""
    url = f"https://engvideo.net/ru/films/?title={movie_name}"
    html = requests.get(url=url, headers=HEADERS)
    data = get_data(html.text, limit=1)
    return data
