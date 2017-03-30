# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

#from scrapy_deltafetch.middleware import DeltaFetch

import logging
import re
from scrapy.exceptions import NotConfigured
from scrapy.exceptions import IgnoreRequest



logger = logging.getLogger(__name__)

class Fake404Error(IgnoreRequest):
    """A fake 404 page response was found and filtered"""

    def __init__(self, response, *args, **kwargs):
        self.response = response
        super(Fake404Error, self).__init__(*args, **kwargs)

class Fake404(object):
    """Spider middleware to drop pages iff they are that annoyance on the web:
       the 404 'not found' response returned as a branded page with HTTP code
       200 (which should indicate success).

       This should not be necessary, both because such behaviour is improper
       on behalf of webservers, and because we are literally crawling the
       sites' OWN LIST OF VALID PAGES. Nevertheless, foxnews.com does it and
       others might.
    """
    def __init__(self, settings):
        if not settings.getbool('FAKE404_ENABLED'):
            raise NotConfigured

        # List of ( url re object, matching xpath ) tuples
        detsigs = settings.get('FAKE404_DETECTIONSIGS')
        self.detectionsigs = [(re.compile(x), y) for x, y in detsigs]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_spider_input(self, response, spider):
        for regex, xp in self.detectionsigs:
            if regex.match(response.url):
                if response.xpath(xp):
                    raise Fake404Error(response,
                                       'Ignoring "not found" response '
                                       'with success HTTP code')
        return None # Success

    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, Fake404Error):
            spider.crawler.stats.inc_value('fake404/response_ignored_count')
            logger.info(
                'Ignoring response from %(response)r: Ignoring "not found" '
                'response with success HTTP code',
                {'response': response}, extra={'spider': spider},
            )
            return []


