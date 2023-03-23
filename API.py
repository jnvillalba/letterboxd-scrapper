from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)


@app.route('/movie', methods=['POST', 'GET'])
def get_movie():
    if request.method == 'GET':
        url = request.args.get('url')
    else:
        data = request.get_json()
        url = data['url']
    name = get_name(url)
    stars = get_stars(url)
    directors = get_director(url)
    writers = get_writers(url)
    year = get_year(url)
    movie = {"name": name, "year": year, "directors": directors, "writers": writers, "stars": stars}
    return jsonify(movie)


def get_name(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        listahtml = soup.find("h1", attrs={"class": "headline-1 js-widont prettify"})
        if listahtml:
            return listahtml.text
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def get_year(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        small_element = soup.find('small', class_='number')
        if small_element:
            return small_element.find('a').text
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def get_stars(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

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
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        project_href = [i['href'] for i in soup.find_all('a', href=True)]
        director = []
        if project_href:
            for x in project_href:
                if "/director/" in x:
                    director_name = x.split("/director/")[1].replace("-", " ").title()
                    director.append(str(director_name.strip('/')))

            return list(set(element for element in director))
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def get_writers(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
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


if __name__ == '__main__':
    app.run(debug=True)
