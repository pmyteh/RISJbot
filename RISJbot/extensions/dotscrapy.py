# -*- coding: utf-8 -*-
import logging
import os
from scrapy_dotpersistence import DotScrapyPersistence
from scrapy import signals
from scrapy.exceptions import NotConfigured

logger = logging.getLogger(__name__)

class FlexibleDotScrapyPersistence(DotScrapyPersistence):
    """A subclass of scrapy_dotpersistence.DotScrapyPersistence (==0.3.0)
       to allow the content to be backed up to our bucket rather than
       ScrapingHub's. Grotty in the absence of a fixed interface.
       
       FIXME: According to the docs at https://support.scrapinghub.com/support/solutions/articles/22000225188-syncing-your-scrapy-folder-to-an-s3-bucket-using-dotscrapy-persistence
              the AWS bucket etc. *can* be overriden using the ADDONS_*
              settings like ADDONS_S3_BUCKET, but only if set spider-by-spider
              rather than for the project as a whole. This seems obviously
              crazy, but may be better than this subclass, which is also
              obviously crazy."""
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        enabled = settings.getbool('FLEXIBLEDOTSCRAPY_ENABLED')
        if not enabled:
            raise NotConfigured
        if  'SCRAPY_JOB' not in os.environ:
            logger.info("Not starting FlexibleDotScrapyPersistence: SCRAPY_JOB"
                            " not configured. Not running on Scrapinghub?")
            raise NotConfigured
        bucket = settings.get('FLEXIBLEDOTSCRAPY_S3_BUCKET')
        return cls(crawler, bucket)

    def __init__(self, crawler, bucket):
        self.AWS_ACCESS_KEY_ID = crawler.settings.get(
            'AWS_ACCESS_KEY_ID')
        self.AWS_SECRET_ACCESS_KEY = crawler.settings.get(
            'AWS_SECRET_ACCESS_KEY')
        self._bucket = bucket
        # Already specialcased by DotScrapyPersistence, so fine to be None. 
        self._bucket_folder = None
        # self._bucket_folder = crawler.settings.get('ADDONS_AWS_USERNAME', '')
        self._projectid = os.environ['SCRAPY_PROJECT_ID']
        self._spider = os.environ['SCRAPY_SPIDER']
        self._localpath = os.environ.get(
            'DOTSCRAPY_DIR', os.path.join(os.getcwd(), '.scrapy/'))
        self._env = {
            'HOME': os.getenv('HOME'),
            'PATH': os.getenv('PATH'),
            'AWS_ACCESS_KEY_ID': self.AWS_ACCESS_KEY_ID,
            'AWS_SECRET_ACCESS_KEY': self.AWS_SECRET_ACCESS_KEY
        }
        self._load_data()
        crawler.signals.connect(self._store_data, signals.engine_stopped)

