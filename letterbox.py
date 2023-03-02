from bs4 import BeautifulSoup
import requests


def get_stars(url):
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, "html.parser")
    listahtml = soup.find("div", attrs={"class": "cast-list text-sluglist"}).find_all("a",
                                                                                      {"class": "text-slug tooltip"})
    star = []
    for x in listahtml:
        nombre_actor = x.text
        star.append(str(nombre_actor))
    return star


# Crear la lista vacía
movies = []
urls = []


def get_director(url):
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, "html.parser")
    # listahtmlD = soup.find("div", attrs={"class": "tabbed-content-block column-block"})\
    #    .find_all("a",{"href": "/director/"})

    project_href = [i['href'] for i in soup.find_all('a', href=True)]
    director = []
    for x in project_href:
        if "/director/" in x:
            director_name = x.split("/director/")[1].replace("-", " ").title()
            director.append(str(director_name.strip('/')))

    return list(set(element for element in director))


def get_writers(url):
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, "html.parser")
    # listahtmlD = soup.find("div", attrs={"class": "tabbed-content-block column-block"})\
    #    .find_all("a",{"href": "/director/"})

    project_href = [i['href'] for i in soup.find_all('a', href=True)]
    director = []
    for x in project_href:
        if "/writer/" in x:
            director_name = x.split("/writer/")[1].replace("-", " ").title()
            director.append(str(director_name.strip('/')))
        if "/writers/" in x:
            director_name = x.split("/writers/")[1].replace("-", " ").title()
            director.append(str(director_name.strip('/')))

    return list(set(element for element in director))


def get_name(url):
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, "html.parser")
    listahtml = soup.find("h1", attrs={"class": "headline-1 js-widont prettify"})
    name = listahtml.text
    return name


lista_python2 = [

                'https://boxd.it/3GBo', 'https://boxd.it/mLsO', 'https://boxd.it/kmg0', 'https://boxd.it/BW1O',
                'https://boxd.it/1D6o', 'https://boxd.it/kv3a', 'https://boxd.it/xvNy', 'https://boxd.it/27ys',
                'https://boxd.it/3wEC', 'https://boxd.it/16sm', 'https://boxd.it/nL2y', 'https://boxd.it/242I',
                'https://boxd.it/1X6e', 'https://boxd.it/nCFc', 'https://boxd.it/npL2', 'https://boxd.it/j5YC',
                'https://boxd.it/wa4K', 'https://boxd.it/7tNa', 'https://boxd.it/1pHK', 'https://boxd.it/1XRu',
                'https://boxd.it/25nW', 'https://boxd.it/tw4c', 'https://boxd.it/1NOK', 'https://boxd.it/7X0M',
                'https://letterboxd.com/film/the-invisible-guardian/',
                'https://letterboxd.com/film/apollo-10-a-space-age-childhood/']


lista_python = ['https://boxd.it/kOf0', 'https://boxd.it/zLxK', 'https://boxd.it/hHpQ', 'https://boxd.it/vfDe',
                'https://boxd.it/270K', 'https://boxd.it/210u', 'https://boxd.it/u8tk', 'https://boxd.it/ezJC',
                'https://boxd.it/ljDs', 'https://boxd.it/duNW', 'https://boxd.it/iwt0', 'https://boxd.it/ifpg',
                'https://boxd.it/27GG', 'https://boxd.it/hjMw', 'https://boxd.it/2beG', 'https://boxd.it/27Gw',
                'https://boxd.it/hXlq', 'https://boxd.it/i7vA', 'https://boxd.it/pAgy', 'https://boxd.it/kjMW',
                'https://boxd.it/wMAk', 'https://boxd.it/21aa', 'https://boxd.it/wJYe', 'https://boxd.it/1Tp2',
                ]


urls = list(lista_python2)
for i, url in enumerate(urls):
    movies.append(
        {"position": i + 1, "name": get_name(url), "director": get_director(url), "writers": get_writers(url)})

# print(movies)
for movie in enumerate(movies):
    print(f"{movie}")
