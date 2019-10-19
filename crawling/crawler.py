from collections import deque
from typing import List, Type, Dict

from scraping.movie_scraper import MovieScraper
from scraping.person_scraper import PersonScraper
from storing.base_storer import BaseStorer
from storing.csv_storer import CsvStorer
from storing.storage_manager import (MovieStorageManager, PersonStorageManager, ProfessionStorageManager,
                                     RoleStorageManager)
from utils import set_locale


class BfsCrawler:

    def __init__(self, storer_class: Type[BaseStorer], storage_dir: str):
        self.movies = dict()

        self.person_deque = deque()
        self.movie_deque = deque()
        self.deques = [self.person_deque, self.movie_deque]

        self.visited_persons = dict()
        self.visited_movies = dict()
        self.visited_professions = dict()
        self.visited = [self.visited_persons, self.visited_movies]

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

    def add_movie(self, movie_url: str):
        self.movies.update({movie_url: self._movie_id})
        self.movie_deque.append((movie_url, self._movie_id))
        self._movie_id += 1

    def scrape_professions(self, person_scraper: PersonScraper, person_id: int) -> Dict[str, int]:
        person_profession_ids = dict()
        professions = person_scraper.professions
        for profession in professions:
            if profession not in self.visited_professions:
                self.profession_manager.storage_profession(self._profession_id, profession)
                self.visited_professions.update({profession: self._profession_id})
                self._profession_id += 1
            self.profession_manager.storage(
                person_profession_id=self._person_profession_id,
                profession_id=self.visited_professions[profession],
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
                if role['movie_url'] in self.movies:
                    movie_id = self.movies[role['movie_url']]
                else:
                    movie_id = self._movie_id
                    self.add_movie(role['movie_url'])
                self.role_manager.storage(
                    role_id=self._role_id,
                    movie_id=movie_id,
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

    def visit(self, url: str, node_id: int) -> List[str]:
        if self.turn:
            neighbours = self.scrape_movie(url, node_id)
        else:
            neighbours = self.scrape_person(url, node_id)
        self.visited[self.turn].update({url: node_id})
        return neighbours

    def crawl(self, movie_url: str):
        self.turn = 1
        self.add_movie(movie_url)
        while not self.is_empty:
            if self.deques[self.turn]:
                url, node_id = self.deques[self.turn].popleft()
                neighbours = self.visit(url, node_id)
                for neighbour in neighbours:
                    if self.visited and neighbour not in self.visited[self.turn - 1]:
                        self.deques[self.turn - 1].append(
                            (neighbour, self._ids[self.turn - 1]))
                        self._ids[self.turn - 1] += 1
            self.turn = (self.turn + 1) % 2


if __name__ == '__main__':
    set_locale()
    crawler = BfsCrawler(storer_class=CsvStorer, storage_dir='../data')
    crawler.crawl(movie_url='https://www.filmweb.pl/Piraci.Z.Karaibow')
