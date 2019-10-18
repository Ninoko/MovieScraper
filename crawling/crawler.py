from collections import deque
from typing import List

from scraping.movie_scraper import MovieScraper
from scraping.person_scraper import PersonScraper


class BfsCrawler:

    def __init__(self):
        self.person_deque = deque()
        self.movie_deque = deque()
        self.deques = [self.person_deque, self.movie_deque]

        self.visited_persons = set()
        self.visited_movies = set()
        self.visited = [self.visited_persons, self.visited_movies]

        self.turn = None

    @property
    def is_empty(self) -> bool:
        return all(map(lambda d: not d, self.deques))

    def scrape_person(self, person_url: str) -> List[str]:
        person_scraper = PersonScraper(person_url=person_url)
        print(person_scraper.full_name())
        professions = person_scraper.professions
        roles = person_scraper.profession_roles(profession=professions[0])
        return [role['movie_url'] for role in roles]

    def scrape_movie(self, movie_url: str) -> List[str]:
        movie_scraper = MovieScraper(movie_url=movie_url)
        print(movie_scraper.title())
        return movie_scraper.cast_links()

    def visit(self, url: str) -> List[str]:
        if self.turn:
            neighbours = self.scrape_movie(url)
        else:
            neighbours = self.scrape_person(url)
        self.visited[self.turn].add(url)
        return neighbours

    def crawl(self, url: str, start_with_movie: bool = True):
        self.turn = int(start_with_movie)
        self.deques[self.turn].append(url)
        while not self.is_empty:
            if self.deques[self.turn]:
                url = self.deques[self.turn].popleft()
                neighbours = self.visit(url)
                for neighbour in neighbours:
                    if neighbour not in self.visited[self.turn - 1]:
                        self.deques[self.turn - 1].append(neighbour)
            self.turn = (self.turn + 1) % 2


if __name__ == '__main__':
    crawler = BfsCrawler()
    crawler.crawl(url='https://www.filmweb.pl/Piraci.Z.Karaibow')
