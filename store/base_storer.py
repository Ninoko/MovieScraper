import os

from abc import ABC, abstractmethod
from typing import List


class BaseStorer(ABC):

    def __init__(self, storage_path: str, column_names: List[str]):
        self.storage_path = storage_path
        self.column_names = column_names
        self.remove_storage()
        self.create_storage()

    def remove_storage(self):
        if os.path.exists(self.storage_path):
            os.remove(self.storage_path)

    @staticmethod
    @abstractmethod
    def extension() -> str:
        pass

    @abstractmethod
    def create_storage(self) -> None:
        pass

    @abstractmethod
    def store(self, record: List):
        pass
