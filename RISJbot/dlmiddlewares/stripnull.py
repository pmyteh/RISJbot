# -*- coding: utf-8 -*-

import logging
from scrapy.http import TextResponse

logger = logging.getLogger(__name__)

class StripNull(object):
    """Downloader middleware to discard ASCII NUL bytes from Responses. This
       really(!) shouldn't be necessary, but bigstory.ap.org/latest (and
       possibly other pages from bigstory.ap.org) are studded with NUL bytes,
       which really messes up the underlying lxml parsing library (which is
       C based and presumably uses null-terminated strings). The effect is that
       the page's parse tree is cut off where the NUL occurs.

       We don't want to do this for possible binaries (like gzip compressed
       sitemaps, for example).

       See: https://github.com/scrapy/scrapy/issues/2481
    """

    def __init__(self, stats, settings):
        if not settings.getbool('STRIPNULL_ENABLED'):
            raise NotConfigured
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats, crawler.settings)

    def process_response(self, request, response, spider):

        if not isinstance(response, TextResponse):
            self.stats.inc_value('stripnull/nottext', spider=spider)
            return response

        newbody = bytes([x for x in response.body if x != 0])

        if len(newbody) < len(response.body):
            self.stats.inc_value('stripnull/stripped', spider=spider)
            return response.replace(body = newbody)
        else:
            self.stats.inc_value('stripnull/clean', spider=spider)
            return response

