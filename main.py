import dill
import click
from crawl.crawler import BfsCrawler

@click.group()
def main():
    pass

@main.command()
@click.option('-m', '--movie_url', help='Url address to filmweb movie site.', default='https://www.filmweb.pl/Piraci.Z.Karaibow', required=True)
@click.option('-s', '--storage_dir', help='Path to director where all data will be stored.', default='../data', required=True)
def start_crawling(movie_url: str, storage_dir: str):
    crawler = BfsCrawler(storage_dir=storage_dir)
    crawler.crawl(movie_url=movie_url)


@main.command()
def continue_crawling():
    crawler = dill.load(open('/tmp/BfsCrawler', 'rb'))
    crawler.crawl()


if __name__ == '__main__':
    main()
