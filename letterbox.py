import json
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup


class MovieScraper:
    """Class to handle movie data scraping from Letterboxd."""

    def __init__(self, timeout: int = 10):
        self.session = requests.Session()
        self.session.timeout = timeout

    def get_html_text(self, url: str) -> Optional[BeautifulSoup]:
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {str(e)}")
            return None

    def get_stars(self, soup: BeautifulSoup) -> List[str]:
        if not soup:
            return []

        cast_list = soup.find("div", class_="cast-list text-sluglist")
        if not cast_list:
            return []

        actors = cast_list.find_all("a", class_="text-slug tooltip")
        return [actor.text.strip() for actor in actors]

    def get_crew(self, soup: BeautifulSoup, role: str) -> List[str]:
        if not soup:
            return []

        project_href = [i['href'] for i in soup.find_all('a', href=True)]
        crew_members = set()

        for href in project_href:
            if f"/{role}/" in href or f"/{role}s/" in href:
                name = href.split(f"/{role}/")[-1].split(f"/{role}s/")[-1]
                name = name.replace("-", " ").title().strip('/')
                crew_members.add(name)

        return list(crew_members)

    def get_name(self, soup: BeautifulSoup) -> Optional[str]:
        if not soup:
            return None

        title_elem = soup.find("h1", class_="headline-1 primaryname")
        return title_elem.text.strip() if title_elem else None

    def get_year(self, soup: BeautifulSoup) -> Optional[str]:
        if not soup:
            return ""

        year_div = soup.find('div', class_='metablock')
        if not year_div:
            return ""

        year_link = year_div.find('a')
        return year_link.text.strip() if year_link else ""

    def scrape_movie(self, url: str) -> Optional[Dict]:
        """
        Scrape movie information and return it as a dictionary.

        Args:
            url: Letterboxd movie URL

        Returns:
            Dictionary with movie information or None if scraping fails
        """
        soup = self.get_html_text(url)
        if not soup:
            return None

        return {
            "name": self.get_name(soup),
            "year": self.get_year(soup),
            "directors": self.get_crew(soup, "director"),
            "writers": self.get_crew(soup, "writer"),
            "actors": self.get_stars(soup)
        }

    def scrape_movies(self, urls: List[str]) -> List[Dict]:
        """
        Scrape multiple movies and return them as a list of dictionaries.

        Args:
            urls: List of Letterboxd movie URLs

        Returns:
            List of dictionaries with movie information
        """
        movies = []
        for url in urls:
            movie = self.scrape_movie(url)
            if movie:
                movies.append(movie)
        return movies


def main():
    urls = [
        'https://letterboxd.com/film/cohen-vs-rosi/',
        'https://letterboxd.com/film/cherry-2021/',
        'https://letterboxd.com/film/resolution/',
    ]

    scraper = MovieScraper()
    movies = scraper.scrape_movies(urls)

    # Imprimir resultados como JSON formateado
    print(json.dumps(movies, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
