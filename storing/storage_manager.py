import os

from typing import Type, List
from abc import ABC, abstractmethod

from storing.base_storer import BaseStorer
from scraping.movie_scraper import MovieScraper
from scraping.person_scraper import PersonScraper


class StorageManager(ABC):

    def __init__(self, storer_class: Type[BaseStorer], storage_dir: str):
        self.storer_class = storer_class
        self.storage_dir = storage_dir
        self.storers = dict()

    def add_storer(self, name: str, column_names: List[str]) -> None:
        storage_path = os.path.join(self.storage_dir, name + self.storer_class.extension())
        self.storers[name] = self.storer_class(
            storage_path=storage_path, column_names=column_names)

    @abstractmethod
    def storage(self, *args, **kwargs) -> None:
        pass


class MovieStorageManager(StorageManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_storer(
            'Movies', ['MovieId', 'Url', 'Title', 'PosterUrl', 'Plot', 'Rating'])

    def storage(self, scraper: MovieScraper, movie_id: int):
        movie_record = [
            movie_id,
            scraper.movie_url,
            scraper.title(),
            scraper.poster_url(),
            scraper.plot(),
            scraper.rating()
        ]
        movie_record = list(map(lambda item: str(item), movie_record))
        self.storers['Movies'].store(movie_record)


class PersonStorageManager(StorageManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_storer(
            'People', ['PersonId', 'Url', 'FullName', 'BirthDate', 'DeathDate', 'ImageUrl'])

    def storage(self, scraper: PersonScraper, person_id: int) -> None:
        person_record = [
            person_id,
            scraper.person_url,
            scraper.full_name(),
            scraper.birth_date(),
            scraper.death_date(),
            scraper.image_url()
        ]
        person_record = list(map(lambda item: str(item), person_record))
        self.storers['People'].store(person_record)


class ProfessionStorageManager(StorageManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_storer(
            'Professions', ['ProfessionId', 'ProfessionName'])
        self.add_storer(
            'PersonProfessions', ['PersonProfessionId', 'PersonId', 'ProfessionId', 'Rating'])

    def storage_profession(self, profession_id: int, profession_name: str) -> None:
        profession_record = [
            profession_id,
            profession_name
        ]
        profession_record = list(map(lambda item: str(item), profession_record))
        self.storers['Professions'].store(profession_record)

    def storage(self, person_profession_id: int, profession_id: int, person_id: int, rating: float):
        person_profession_record = [
            person_profession_id,
            person_id,
            profession_id,
            rating
        ]
        person_profession_record = list(map(lambda item: str(item), person_profession_record))
        self.storers['PersonProfessions'].store(person_profession_record)


class RoleStorageManager(StorageManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_storer(
            'Roles', ['RoleId', 'PersonProfessionId', 'MovieId', 'RoleName'])

    def storage(self,
                role_id: int,
                person_profession_id: int,
                movie_id: int,
                role_name: str) -> None:
        person_record = [
            role_id,
            person_profession_id,
            movie_id,
            role_name
        ]
        person_record = list(map(lambda item: str(item), person_record))
        self.storers['Roles'].store(person_record)
