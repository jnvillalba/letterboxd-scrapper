import requests
from bs4 import BeautifulSoup


def get_html_text(url):
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, "html.parser")
    return soup


def get_stars(url):
    try:
        soup = get_html_text(url)

        cast_list = soup.find("div", attrs={"class": "cast-list text-sluglist"})
        if cast_list:
            listahtml = cast_list.find_all("a", {"class": "text-slug tooltip"})
        else:
            listahtml = None

        star = []
        if listahtml:
            for x in listahtml:
                nombre_actor = x.text
                star.append(str(nombre_actor))
            return star
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def get_director(url):
    soup = get_html_text(url)
    project_href = [i['href'] for i in soup.find_all('a', href=True)]
    director = []
    for x in project_href:
        if "/director/" in x:
            director_name = x.split("/director/")[1].replace("-", " ").title()
            director.append(str(director_name.strip('/')))

    return list(set(element for element in director))


def get_writers(url):
    try:
        soup = get_html_text(url)
        project_href = [i['href'] for i in soup.find_all('a', href=True)]
        director = []
        if project_href:
            for x in project_href:
                if "/writer/" in x:
                    director_name = x.split("/writer/")[1].replace("-", " ").title()
                    director.append(str(director_name.strip('/')))
                if "/writers/" in x:
                    director_name = x.split("/writers/")[1].replace("-", " ").title()
                    director.append(str(director_name.strip('/')))

            return list(set(element for element in director))
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def get_name(url):
    soup = get_html_text(url)
    listahtml = soup.find("h1", attrs={"class": "headline-1 filmtitle"})
    if listahtml:
        name = listahtml.text
        return name
    else:
        return None


def get_year(url):
    soup = get_html_text(url)
    small_element = soup.find('div', class_='releaseyear')
    if small_element:
        year = small_element.find('a').text
        return year
    else:
        return None


lista = [
    'https://letterboxd.com/film/25th-hour/',
]

movies = []

for i, url in enumerate(lista):
    movies.append(
        {"name": get_name(url), "year": get_year(url),
         "directors": get_director(url),
         "writers": get_writers(url), "actors": get_stars(url)})

for movie in movies:
    print(movie)
