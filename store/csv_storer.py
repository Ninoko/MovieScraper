import os
import csv

from typing import List

from store.base_storer import BaseStorer


class CsvStorer(BaseStorer):

    @staticmethod
    def extension() -> str:
        return '.csv'

    def create_storage(self) -> None:
        dir_path = os.path.dirname(self.storage_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(self.storage_path, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(self.column_names)
        file.close()

    def store(self, record: List):
        with open(self.storage_path, 'a') as file:
            writer = csv.writer(file)
            writer.writerow(record)
        file.close()
