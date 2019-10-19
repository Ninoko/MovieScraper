from setuptools import setup, find_packages

setup(
    name='scraping',
    version='1.0.0',
    author='Miłosz Michta',
    author_email='milosz.casper.michta@gmail.com',
    description='Python package for movie data scraping',
    packages=find_packages(include=['scraping', 'crawling', 'storing']),
    install_requires=(
        'bs4',
        'requests',
    ),
)
