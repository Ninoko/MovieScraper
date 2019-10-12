from datetime import datetime
from typing import Dict, Any, List

from bs4 import BeautifulSoup

from scraping.base_scraper import BaseScraper
from scraping.utils import safe_return, set_locale


class PersonScraper(BaseScraper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.person_soup = None

    @safe_return
    def get_full_name(self, person_soup: BeautifulSoup) -> str:
        return person_soup.find('h1', {'class', 'personName'}).text

    @safe_return
    def get_image_url(self, person_soup: BeautifulSoup) -> str:
        return person_soup.find('img', {'itemprop': 'image'})['src']

    @safe_return
    def get_birth_date(self, person_soup: BeautifulSoup) -> datetime.date:
        return datetime.strptime(
            person_soup.find(
                'span', {'itemprop': 'birthDate'}
            ).text.strip(), '%d %B %Y').date()

    @safe_return
    def get_death_date(self, person_soup: BeautifulSoup) -> datetime.date:
        return datetime.strptime(
            person_soup.find(
                'span', {'itemprop': 'deathDate'}
            ).text.strip(), '%d %B %Y').date()

    def person_description(self, person_url: str) -> Dict[str, Any]:
        self.person_soup = self.get_soup(person_url)
        return {
            'name': self.get_full_name(self.person_soup),
            'birth_date': self.get_birth_date(self.person_soup),
            'death_date': self.get_death_date(self.person_soup),
            'image_url': self.get_image_url(self.person_soup),
        }


class ActorScraper(PersonScraper):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @safe_return
    def get_rating(self, actor_soup: BeautifulSoup) -> float:
        return float(
            actor_soup.find('div', {'data-prof': 'actors'})
                      .find('span', {'itemprop': 'ratingValue'})
                      .text.replace(',', '.'))

    @safe_return(exception=AttributeError)
    def _get_role_name(self, role_soup: BeautifulSoup) -> str:
        return role_soup.find('td', {'class', 'rt'}).find('p', {'class', 'roleText'}).text

    def get_role(self, role_soup: BeautifulSoup) -> Dict[str, Any]:
        movie = role_soup.find('td', {'class', 'ft'}).find('a')
        return {
            'movie_title': movie.text,
            'movie_url': f'{self.website}{movie["href"].strip()}',
            'role_name': self._get_role_name(role_soup)}

    def get_roles(self, actor_soup) -> List[Dict[str, Any]]:
        rows = actor_soup.find('tbody', attrs={'data-profession': 'actors'}).find_all('tr')
        return [self.get_role(row) for row in rows]

    def actor_description(self, actor_url: str) -> Dict[str, Any]:
        person_description = super().person_description(actor_url)
        return {
            'rating': self.get_rating(self.person_soup),
            'roles': self.get_roles(self.person_soup),
            **person_description
        }


if __name__ == '__main__':
    set_locale()
    actor_scraper = ActorScraper()
    desc = actor_scraper.actor_description("https://www.filmweb.pl/person/Johnny.Depp")
    for role in desc['roles']:
        print(f'{desc["name"]} play in the {role["movie_title"]} as {role["role_name"]}')
    print(desc.keys())
    print(desc['rating'])
    print(desc['birth_date'])
