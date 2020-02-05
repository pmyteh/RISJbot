# -*- coding: utf-8 -*-
import logging
from scrapy.spiders import Spider
from scrapy.http import Request

logger = logging.getLogger(__name__)

# This spider is a base for those attempting to crawl and parse a specified
# list of URLs rather than using an RSS feed or a sitemap. It needs the
# SPECIFIED_URIS_FILE setting set up to point to a file with a list of URLs.
class NewsSpecifiedSpider(Spider):
    start_urls = []

    def start_requests(self):
        if self.crawler.settings.get('REFETCHCONTROL_ENABLED') == True:
            logger.warning('RefetchControl is incompatible with '
                           'NewsSpecifiedSpider and will give spurious '
                           'warnings. Try setting REFETCHCONTROL_ENABLED to '
                           'False in settings.py.')

        startfn = self.crawler.settings.get('SPECIFIED_URLS_FILE')
        if not startfn:
            logger.critical("SPECIFIED_URLS_FILE must be configured (e.g. in "
                            "settings.py) to point to a file containing a "
                            "list of URLs.")
            return

        for url in self.start_urls:
            yield Request(url, dont_filter=True)

        with open(startfn, 'r') as f:
            urls = [u.strip() for u in f.readlines()]
            logger.debug(f"URLs read from SPECIFIED_URL_FILE: {urls}")
            for url in urls:
                if url != '':
                    yield Request(url, dont_filter=True)

    def parse(self, response):
        return self.parse_page(response)

    def parse_page(self, response):
        raise NotImplementedError

