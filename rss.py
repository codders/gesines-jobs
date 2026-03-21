import os
import sys

from dotenv import load_dotenv
from feedgen.feed import FeedGenerator

from jobs import JobSearcher

load_dotenv()

class FeedBuilder:

    def __init__(self):
        self.fg = FeedGenerator()
        self.fg.id(os.getenv('RSS_ID_URL'))
        self.fg.title('Jenny\'s Jobs')
        self.fg.author({ 'name': os.getenv('RSS_FEED_AUTHOR_NAME'), 'email': os.getenv('RSS_FEED_AUTHOR_EMAIL') })
        self.fg.link(href=os.getenv('RSS_FEED_ALTERNATE_URL'), rel='alternate')
        self.fg.subtitle('Jobs in Berlin and Marburg')
        self.fg.language('de')

    def add_job_entry(self, job):
        entry = self.fg.add_entry()
        entry.id(job.refnr)
        entry.title(job.get_title())
        job_url = job.url
        if job_url is not None:
            entry.link(href=job_url)
        entry.description(f"Matches {",".join(job.matches)} Published {job.publish_date}")
        entry.content(job.details)

    def dump_rss(self):
        sys.stdout.write(self.fg.rss_str(pretty=True).decode('utf-8'))

if __name__ == "__main__":
    searcher = JobSearcher()
    feed_builder = FeedBuilder()
    for job in searcher.run_job_search():
        feed_builder.add_job_entry(job)
    feed_builder.dump_rss()


