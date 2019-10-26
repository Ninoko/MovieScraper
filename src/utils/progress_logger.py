from tqdm import tqdm


class ProgressLogger:

    def __init__(self, desc: str):
        self.desc = desc
        self.progress_bar_percentage = tqdm(desc=f'Scraped {desc}', unit='%', total=100.0)

    def update(self, queued, finished):
        self.progress_bar_percentage.n = finished
        self.progress_bar_percentage.total = queued
        self.progress_bar_percentage.refresh()
