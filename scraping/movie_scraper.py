from typing import List

from bs4 import BeautifulSoup

from scraping.base_scraper import BaseScraper
from utils import safe_return


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
        return self.movie_soup.find('h1', {'class', 'filmTitle'}).text.strip()

    @safe_return
    def poster_url(self) -> str:
        return self.movie_soup.find('img', {'itemprop': 'image'})['src']

    @safe_return
    def plot(self) -> str:
        return self.movie_soup.find('div', {'class': 'filmPlot'}).text

    @safe_return
    def rating(self) -> float:
        return float(
            self.movie_soup.find('div', {'class': 'filmRateBox'})
                           .find('span', {'itemprop': 'ratingValue'})
                .text.strip().replace(',', '.'))

    def person_link(self, row_soup: BeautifulSoup) -> str:
        anchor = row_soup.find('a', {'rel': 'v:starring'})
        return f'{self.website}{anchor["href"].strip()}'

    def cast_links(self) -> List[str]:
        actor_rows = self.actors_soup.find_all('tr', {'data-role': True})
        crew_rows = self.crew_soup.find_all('tr', {'data-role': True})
        return list(set([self.person_link(row) for row in actor_rows]
                        + [self.person_link(row) for row in crew_rows]))
