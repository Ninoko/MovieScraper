import locale
from itertools import chain
from datetime import datetime, date
from typing import Dict, Any, List, Optional

from bs4 import BeautifulSoup

from scrape.base_scraper import BaseScraper
from utils.utils import safe_return


class PersonScraper(BaseScraper):

    def __init__(self, person_url: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.person_url = person_url
        self.person_soup = self.get_soup(self.person_url)
        self._professions = None

        locale.setlocale(locale.LC_TIME, 'pl_PL.UTF-8')

    @property
    @safe_return(exception=(AttributeError, TypeError), default_return=[])
    def professions(self) -> Optional[List[str]]:
        if self._professions is None:
            _professions = self.person_soup.find('table', {'class': 'filmographyTable'})\
                                           .find_all('thead', {'data-profession': True})
            self._professions = [profession['data-profession'] for profession in _professions]
        return self._professions

    @safe_return
    def full_name(self) -> str:
        return self.person_soup.find('h1', {'class', 'personName'}).text

    @safe_return
    def image_url(self) -> str:
        return self.person_soup.find('img', {'itemprop': 'image'})['src']

    @safe_return
    def birth_date(self) -> date:
        return datetime.strptime(
            self.person_soup.find(
                'span', {'itemprop': 'birthDate'}
            ).text.strip(), '%d %B %Y').date()

    @safe_return
    def death_date(self) -> date:
        return datetime.strptime(
            self.person_soup.find(
                'span', {'itemprop': 'deathDate'}
            ).text.strip(), '%d %B %Y').date()

    @safe_return
    def profession_rating(self, profession: str) -> float:
        return float(
            self.person_soup.find('div', {'data-prof': profession})
                            .find('span', {'itemprop': 'ratingValue'})
                            .text.replace(',', '.'))

    @safe_return(exception=AttributeError)
    def _role_name(self, role_soup: BeautifulSoup) -> str:
        return role_soup.find('td', {'class', 'rt'}).find('p', {'class', 'roleText'}).text

    def _role(self, role_soup: BeautifulSoup) -> Dict[str, Any]:
        movie = role_soup.find('td', {'class', 'ft'}).find('a')
        return {
            'movie_url': f'{self.website}{movie["href"].strip()}',
            'role_name': self._role_name(role_soup)
        }

    def split_roles(self, role: Dict[str, Any]) -> List[Dict[str, Any]]:
        if role['role_name'] and '/' in role['role_name']:
            roles = []
            for role_name in role['role_name'].split('/'):
                roles.append({
                    'movie_url': role['movie_url'],
                    'role_name': role_name.strip()
                })
            return roles
        else:
            return [role]

    def profession_roles(self, profession: str) -> List[Dict[str, Any]]:
        rows = self.person_soup.find(
            'tbody', {'data-profession': profession}
        ).find_all('tr')
        roles = [self.split_roles(self._role(row)) for row in rows]
        return list(chain(*roles))

    def movies_involved_in(self) -> List[str]:
        movies: List[str] = []
        for profession in self.professions:
            _roles = self.profession_roles(profession)
            movies.extend(role['movie_url'] for role in _roles)
        return list(set(movies))
