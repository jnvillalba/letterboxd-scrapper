import json
import logging
import random
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)


def get_stars(soup: BeautifulSoup) -> List[str]:
    if not soup:
        return []

    cast_list = soup.find("div", class_="cast-list text-sluglist")
    if not cast_list:
        return []

    actors = cast_list.find_all("a", class_="text-slug tooltip")
    return [actor.text.strip() for actor in actors]


def get_crew(soup: BeautifulSoup, role: str) -> List[str]:
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


def get_name(soup: BeautifulSoup) -> Optional[str]:
    if not soup:
        return None

    # First try to get the original name
    original_name = soup.find("h2", class_="originalname")
    if original_name:
        return original_name.text.strip()

    # If original name doesn't exist, fall back to title element
    title_elem = soup.find("h1", class_="headline-1 primaryname")
    if title_elem:
        return title_elem.text.strip()

    # If neither exists, return None
    return None


def get_year(soup: BeautifulSoup) -> Optional[str]:
    if not soup:
        return ""

    productioninfo_div = soup.find('div', class_='productioninfo')
    if not productioninfo_div:
        return None

    year_link = productioninfo_div.find('a')

    return year_link.text.strip() if year_link else ""

    # year_div = soup.find('div', class_='metablock')
    # if not year_div:
    #     return ""
    #
    # year_link = year_div.find('a')
    # return year_link.text.strip() if year_link else ""


class MovieScraper:
    """Class to handle movie data scraping from Letterboxd."""

    def __init__(
        self,
        timeout: int = 10,
        max_attempts: int = 4,
        backoff: float = 1.0,
        preflight: bool = True,
    ):
        # Guardar timeout y configurar cabeceras para simular un navegador
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.backoff = backoff
        self.preflight = preflight
        self.session = requests.Session()
        self.failures: List[Dict] = []
        self._attempts_by_url: Dict[str, int] = {}

        if timeout <= 0:
            raise ValueError("timeout debe ser mayor que cero")
        if max_attempts <= 0:
            raise ValueError("max_attempts debe ser mayor que cero")
        if backoff < 0:
            raise ValueError("backoff no puede ser negativo")

        # Lista simple de User-Agents para rotar en caso de bloqueos
        self._user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/115.0"
        ]

        # Cabeceras base
        self.session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Referer": "https://letterboxd.com/",
            "Upgrade-Insecure-Requests": "1",
        })

        # Marcar si hicimos la petición a la home para obtener cookies
        self._preflight_done = False
        self._preflight_attempted = False

        # Seleccionar un User-Agent inicial
        self.session.headers.update({"User-Agent": random.choice(self._user_agents)})

    def _do_preflight(self) -> None:
        """Hacer una petición a la home para obtener cookies y cabeceras que el servidor pueda esperar."""
        self._preflight_attempted = True
        try:
            # Cambiar User-Agent antes de la preflight para simular navegador diferente ocasionalmente
            self.session.headers.update({"User-Agent": random.choice(self._user_agents)})
            response = self.session.get("https://letterboxd.com/", timeout=self.timeout)
            response.raise_for_status()
            self._preflight_done = True
        except requests.exceptions.RequestException as error:
            # La película todavía puede estar disponible aunque falle la home.
            logger.warning("Preflight falló; se continuará sin cookies: %s", error)

    @staticmethod
    def _retry_after_seconds(response: requests.Response, fallback: float) -> float:
        """Obtener la espera indicada por el servidor o usar el backoff calculado."""
        retry_after = response.headers.get("Retry-After")
        if not retry_after:
            return fallback

        try:
            return max(0.0, float(retry_after))
        except ValueError:
            try:
                retry_at = parsedate_to_datetime(retry_after)
                if retry_at.tzinfo is None:
                    retry_at = retry_at.replace(tzinfo=timezone.utc)
                return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())
            except (TypeError, ValueError, OverflowError):
                return fallback

    def _record_failure(
        self,
        url: str,
        error: str,
        attempts: int,
        started_at: float,
        status_code: Optional[int] = None,
    ) -> None:
        failure = {
            "url": url,
            "error": error,
            "attempts": attempts,
            "elapsed_seconds": round(time.perf_counter() - started_at, 2),
        }
        if status_code is not None:
            failure["status_code"] = status_code
        self.failures.append(failure)
        logger.error(
            "No se pudo scrapear %s después de %d intento(s): %s",
            url,
            attempts,
            error,
        )

    def get_html_text(self, url: str) -> Optional[BeautifulSoup]:
        """Descargar una página usando una única política de reintentos."""
        started_at = time.perf_counter()
        retryable_statuses = {403, 429, 500, 502, 503, 504}

        if self.preflight and not self._preflight_attempted:
            self._do_preflight()

        for attempt in range(1, self.max_attempts + 1):
            self._attempts_by_url[url] = attempt
            try:
                # Rotar User-Agent ocasionalmente
                if attempt > 1:
                    self.session.headers.update({"User-Agent": random.choice(self._user_agents)})

                response = self.session.get(url, timeout=self.timeout)

                if response.status_code in retryable_statuses:
                    error = f"HTTP {response.status_code} {response.reason}"
                    if attempt == self.max_attempts:
                        self._record_failure(
                            url, error, attempt, started_at, response.status_code
                        )
                        return None

                    fallback = self.backoff * (2 ** (attempt - 1))
                    wait_seconds = self._retry_after_seconds(response, fallback)
                    logger.warning(
                        "%s en %s (intento %d/%d); reintentando en %.1fs",
                        error,
                        url,
                        attempt,
                        self.max_attempts,
                        wait_seconds,
                    )
                    time.sleep(wait_seconds)
                    continue

                response.raise_for_status()
                return BeautifulSoup(response.text, "html.parser")

            except requests.exceptions.HTTPError as error:
                # 4xx no incluidos arriba son permanentes (por ejemplo, 404).
                status_code = (
                    error.response.status_code
                    if error.response is not None
                    else None
                )
                self._record_failure(
                    url, str(error), attempt, started_at, status_code
                )
                return None
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as error:
                error_name = type(error).__name__
                message = f"{error_name}: {error}"
                if attempt == self.max_attempts:
                    self._record_failure(url, message, attempt, started_at)
                    return None

                wait_seconds = self.backoff * (2 ** (attempt - 1))
                logger.warning(
                    "%s en %s (intento %d/%d); reintentando en %.1fs",
                    error_name,
                    url,
                    attempt,
                    self.max_attempts,
                    wait_seconds,
                )
                time.sleep(wait_seconds)
            except requests.exceptions.RequestException as error:
                self._record_failure(url, str(error), attempt, started_at)
                return None

        return None

    def scrape_movie(self, url: str) -> Optional[Dict]:
        """
        Scrape movie information and return it as a dictionary.

        Args:
            url: Letterboxd movie URL

        Returns:
            Dictionary with movie information or None if scraping fails
        """
        started_at = time.perf_counter()
        soup = self.get_html_text(url)
        if not soup:
            return None

        movie = {
            "name": get_name(soup),
            "year": get_year(soup),
            "directors": get_crew(soup, "director"),
            "writers": get_crew(soup, "writer"),
            "actors": get_stars(soup)
        }

        if movie["name"] is None:
            self._record_failure(
                url,
                "HTML inesperado: no se encontró el título de la película",
                self._attempts_by_url.get(url, 1),
                started_at,
            )
            return None

        return movie

    def scrape_movies(self, urls: List[str]) -> List[Dict]:
        """
        Scrape multiple movies and return them as a list of dictionaries.

        Args:
            urls: List of Letterboxd movie URLs

        Returns:
            List of dictionaries with movie information
        """
        self.failures.clear()
        self._attempts_by_url.clear()
        started_at = time.perf_counter()
        movies = []
        for url in urls:
            movie = self.scrape_movie(url)
            if movie:
                movies.append(movie)

        logger.info(
            "Scraping terminado: %d correctas, %d fallidas, %.2f segundos",
            len(movies),
            len(self.failures),
            time.perf_counter() - started_at,
        )
        return movies

    def close(self) -> None:
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    urls = [
        'https://letterboxd.com/film/one-night-only-2026/'
    ]

    with MovieScraper() as scraper:
        movies = scraper.scrape_movies(urls)

    # Imprimir resultados como JSON formateado
    print(json.dumps(movies, indent=2, ensure_ascii=False))

    if scraper.failures:
        logger.error("Detalle de fallos:\n%s", json.dumps(scraper.failures, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
