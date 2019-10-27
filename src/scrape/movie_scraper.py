from typing import List

from bs4 import BeautifulSoup

from scrape.base_scraper import BaseScraper
from utils.utils import safe_return


class MovieScraper(BaseScraper):

    def __init__(self, movie_url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.movie_url = movie_url
        self.movie_soup = self.get_soup(self.movie_url)
        self.actors_soup = self.get_soup(self.movie_url + '/cast/actors')
        self.crew_soup = self.get_soup(self.movie_url + '/cast/crew')

    @safe_return
    def title(self) -> str:
        return self.movie_soup.find(
            'h1', {'class', 'filmTitle'}
            ).find('a')['title'].strip()

    @safe_return
    def year(self) -> int:
        text = self.movie_soup.find(
            'h1', {'class', 'filmTitle'}
            ).find(
                'span', {'class': 'halfSize'}
                ).text
        text = text[text.find("(")+1:text.find(")")].split('-')[0]
        text = ''.join([char for char in text if char.isdigit()])
        return int(text)

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

    @safe_return(exception=AttributeError)
    def cast_links(self) -> List[str]:
        try:
            actor_rows = self.actors_soup.find('form', {'class', 'filmCastWrapper'})\
                                         .find_all('tr', {'data-role': True})
            crew_rows = self.crew_soup.find('form', {'class', 'filmCastWrapper'})\
                                      .find_all('tr', {'data-role': True})
        except AttributeError:
            actor_rows = self.movie_soup.find('div', {'class', 'filmCastWrapper'})\
                                        .find_all('tr', {'class': 'cast'})
            crew_rows = self.movie_soup.find('div', {'class', 'filmCastWrapper'})\
                                       .find_all('tr', {'class': 'creator'})
        return list(set([self.person_link(row) for row in actor_rows]
                        + [self.person_link(row) for row in crew_rows]))
