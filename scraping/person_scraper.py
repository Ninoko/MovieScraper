from datetime import datetime
from typing import Dict, Any, List

from bs4 import BeautifulSoup

from scraping.base_scraper import BaseScraper
from scraping.utils import safe_return, set_locale


class PersonScraper(BaseScraper):

    def __init__(self, person_url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.person_url = person_url
        self._person_soup = None
        self._professions = None

    @property
    def person_soup(self) -> BeautifulSoup:
        if self._person_soup is None:
            self._person_soup = self.get_soup(self.person_url)
        return self._person_soup\

    @property
    def professions(self) -> List[str]:
        if self._professions is None:
            _professions = self.person_soup.find(
                'div', {'class': 'communityRate'}
            ).find_all('div', id=lambda id: id and id.startswith('pr_'), recursive=False)
            self._professions = [profession['data-prof'] for profession in _professions]
        return self._professions

    @safe_return
    def get_full_name(self) -> str:
        return self.person_soup.find('h1', {'class', 'personName'}).text

    @safe_return
    def get_image_url(self) -> str:
        return self.person_soup.find('img', {'itemprop': 'image'})['src']

    # @safe_return
    def get_birth_date(self) -> datetime.date:
        return datetime.strptime(
            self.person_soup.find(
                'span', {'itemprop': 'birthDate'}
            ).text.strip(), '%d %B %Y').date()

    @safe_return
    def get_death_date(self) -> datetime.date:
        return datetime.strptime(
            self.person_soup.find(
                'span', {'itemprop': 'deathDate'}
            ).text.strip(), '%d %B %Y').date()

    def get_person_description(self) -> Dict[str, Any]:
        return {
            'name': self.get_full_name(),
            'birth_date': self.get_birth_date(),
            'death_date': self.get_death_date(),
            'image_url': self.get_image_url(),
        }

    @safe_return
    def get_rating(self, profession: str) -> float:
        return float(
            self.person_soup.find('div', {'data-prof': profession})
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

    def get_roles(self, profession: str) -> List[Dict[str, Any]]:
        rows = self.person_soup.find(
            'tbody', attrs={'data-profession': profession}
        ).find_all('tr')
        return [self.get_role(row) for row in rows]

    def get_profession_description(self, profession: str) -> Dict[str, Any]:
        return {
            'rating': self.get_rating(profession),
            'roles': self.get_roles(profession),
        }

    def get_description(self):
        return {
            **self.get_person_description(),
            'professions': {
                profession: self.get_profession_description(profession)
                for profession in self.professions
            }
        }


if __name__ == '__main__':
    set_locale()
    actor_scraper = PersonScraper("https://www.filmweb.pl/person/Johnny.Depp")
    desc = actor_scraper.get_description()
    print(desc.keys())
    print(desc['birth_date'])
    for prof in desc['professions']:
        print(prof)
        print(desc['professions'][prof])
