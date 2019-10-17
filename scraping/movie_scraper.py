from datetime import datetime
from typing import Dict, Any, List

from bs4 import BeautifulSoup

from scraping.base_scraper import BaseScraper
from scraping.utils import safe_return, set_locale


class MovieScraper(BaseScraper):

    def __init__(self, movie_url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.movie_url = movie_url
        self._movie_soup = None
        self._actors_soup = None
        self._crew_soup = None

    @property
    def movie_soup(self) -> BeautifulSoup:
        if self._movie_soup is None:
            self._movie_soup = self.get_soup(self.movie_url)
        return self._movie_soup

    @property
    def actors_soup(self) -> BeautifulSoup:
        if self._actors_soup is None:
            self._actors_soup = self.get_soup(self.movie_url + '/cast/actors')
        return self._actors_soup

    @property
    def crew_soup(self) -> BeautifulSoup:
        if self._crew_soup is None:
            self._crew_soup = self.get_soup(self.movie_url + '/cast/crew')
        return self._crew_soup

    @safe_return
    def title(self) -> str:
        return self.movie_soup.find('h1', {'class', 'filmTitle'}).text

    @safe_return
    def poster_url(self) -> str:
        return self.movie_soup.find('img', {'itemprop': 'image'})['src']\

    @safe_return
    def plot(self) -> str:
        return self.movie_soup.find('div', {'class': 'filmPlot'}).text

    @safe_return
    def rating(self) -> float:
        return float(
            self.movie_soup.find('span', {'class': 'ratingRateValue'})
                           .text.replace(',', '.'))

    def _role(self, row_soup: BeautifulSoup) -> Dict[str, str]:
        anchor = row_soup.find('a', {'rel': 'v:starring'})
        return {
            'person_name': anchor['title'],
            'person_url': f'{self.website}{anchor["href"]}',
            'role_name': row_soup.find('span', {'class': None}).text,
        }

    def roles(self) -> List[Dict[str, str]]:
        rows = self.actors_soup.find_all('tr', {'data-role': True})
        return [self._role(row) for row in rows]


if __name__ == '__main__':
    set_locale()
    scraper = MovieScraper('https://www.filmweb.pl/Piraci.Z.Karaibow')
    print(scraper.roles())
