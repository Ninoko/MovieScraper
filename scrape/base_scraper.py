import requests
from requests.adapters import HTTPAdapter

from abc import ABC
from bs4 import BeautifulSoup

from crawl.utils import safe_return


class BaseScraper(ABC):

    def __init__(self, *args, **kwargs):
        self.website = 'https://www.filmweb.pl'
        self.args = args
        self.kwargs = kwargs
        self.session = requests.Session()
        self.session.mount(
            self.website, HTTPAdapter())

    @safe_return(exception=requests.exceptions.RequestException)
    def get_soup(self, page_url: str) -> BeautifulSoup:
        while True:
            request = self.session.get(page_url)
            soup = BeautifulSoup(request.content, 'html.parser')
            if soup is not None:
                return soup
