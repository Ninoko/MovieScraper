from collections import deque
from typing import List, Type, Dict

from scrape.movie_scraper import MovieScraper
from scrape.person_scraper import PersonScraper
from store.base_storer import BaseStorer
from store.csv_storer import CsvStorer
from store.storage_manager import (MovieStorageManager, PersonStorageManager, ProfessionStorageManager,
                                   RoleStorageManager)
from crawl.utils import set_locale


class BfsCrawler:

    def __init__(self, storage_dir: str, storer_class: Type[BaseStorer] = CsvStorer):
        self.person_set = dict()
        self.movie_set = dict()
        self.profession_set = dict()
        self.sets = [self.person_set, self.movie_set]

        self.person_deque = deque()
        self.movie_deque = deque()
        self.deques = [self.person_deque, self.movie_deque]

        self.movie_manager = MovieStorageManager(
            storer_class=storer_class, storage_dir=storage_dir)
        self.person_manager = PersonStorageManager(
            storer_class=storer_class, storage_dir=storage_dir)
        self.profession_manager = ProfessionStorageManager(
            storer_class=storer_class, storage_dir=storage_dir)
        self.role_manager = RoleStorageManager(
            storer_class=storer_class, storage_dir=storage_dir)

        self._person_id = 1
        self._movie_id = 1
        self._person_profession_id = 1
        self._profession_id = 1
        self._role_id = 1
        self._ids = [self._person_id, self._movie_id]

        self.turn = None

    @property
    def is_empty(self) -> bool:
        return all(map(lambda d: not d, self.deques))

    def add_profession(self, profession: str):
        self.profession_manager.storage_profession(self._profession_id, profession)
        self.profession_set.update({profession: self._profession_id})
        self._profession_id += 1

    def add_movie(self, movie_url: str):
        self.movie_set.update({movie_url: self._movie_id})
        self.movie_deque.append((movie_url, self._movie_id))
        self._movie_id += 1

    def add_person(self, person_url: str):
        self.person_set.update({person_url: self._person_id})
        self.person_deque.append((person_url, self._person_id))
        self._person_id += 1

    def add_node(self, node_url: str) -> None:
        if self.turn:
            self.add_person(node_url)
        else:
            self.add_movie(node_url)

    def get_movie_id(self, movie_url: str) -> int:
        if movie_url in self.movie_set:
            movie_id = self.movie_set[movie_url]
        else:
            movie_id = self._movie_id
            self.add_movie(movie_url)
        return movie_id

    def scrape_professions(self, person_scraper: PersonScraper, person_id: int) -> Dict[str, int]:
        person_profession_ids = dict()
        professions = person_scraper.professions
        for profession in professions:
            if profession not in self.profession_set:
                self.add_profession(profession)
            self.profession_manager.storage(
                person_profession_id=self._person_profession_id,
                profession_id=self.profession_set[profession],
                person_id=person_id,
                rating=person_scraper.profession_rating(profession))
            person_profession_ids[profession] = self._person_profession_id
            self._person_profession_id += 1
        return person_profession_ids

    def scrape_roles(self,
                     person_scraper: PersonScraper,
                     person_profession_ids: Dict[str, int]) -> None:
        professions = person_scraper.professions

        for profession in professions:
            roles = person_scraper.profession_roles(profession)
            for role in roles:
                self.role_manager.storage(
                    role_id=self._role_id,
                    movie_id=self.get_movie_id(role['movie_url']),
                    person_profession_id=person_profession_ids[profession],
                    role_name=role['role_name'])
                self._role_id += 1

    def scrape_person(self, person_url: str, person_id: int) -> List[str]:
        person_scraper = PersonScraper(person_url=person_url)
        person_profession_ids = self.scrape_professions(person_scraper, person_id)
        self.scrape_roles(person_scraper, person_profession_ids)
        self.person_manager.storage(person_scraper, person_id)
        return person_scraper.movies_involved_in()

    def scrape_movie(self, movie_url: str, movie_id: int) -> List[str]:
        movie_scraper = MovieScraper(movie_url=movie_url)
        self.movie_manager.storage(movie_scraper, movie_id)
        return movie_scraper.cast_links()

    def get_neighbours(self, url: str, node_id: int) -> List[str]:
        if self.turn:
            return self.scrape_movie(url, node_id)
        else:
            return self.scrape_person(url, node_id)

    def is_new(self, node_url: str):
        return node_url not in self.sets[self.turn - 1]

    def crawl(self, movie_url: str):
        self.turn = 1
        self.add_movie(movie_url)
        while not self.is_empty:
            if self.deques[self.turn]:
                url, node_id = self.deques[self.turn].popleft()
                neighbours = self.get_neighbours(url, node_id)
                for neighbour in neighbours:
                    if self.is_new(neighbour):
                        self.add_node(neighbour)
            self.turn = (self.turn + 1) % 2


if __name__ == '__main__':
    set_locale()
    crawler = BfsCrawler(storage_dir='../data')
    crawler.crawl(movie_url='https://www.filmweb.pl/Piraci.Z.Karaibow')
