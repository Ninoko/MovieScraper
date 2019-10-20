from setuptools import setup, find_packages

setup(
    name='movie-scraper',
    version='1.0.0',
    author='Miłosz Michta',
    author_email='milosz.casper.michta@gmail.com',
    packages=find_packages(),
    install_requires=(
        'bs4',
        'requests',
    ),
)
