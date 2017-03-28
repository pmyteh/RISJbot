# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)

class RISJStripNull(object):
    """Downloader middleware to discard ASCII NUL bytes from Responses. This
       really(!) shouldn't be necessary, but bigstory.ap.org/latest (and
       possibly other pages from bigstory.ap.org) are studded with NUL bytes,
       which really messes up the underlying lxml parsing library (which is
       C based and presumably uses null-terminated strings). The effect is that
       the page's parse tree is cut off where the NUL occurs.
    """

    def __init__(self, stats, settings):
        if not settings.getbool('RISJSTRIPNULL_ENABLED'):
            raise NotConfigured
        self.spiders = settings.get('RISJSTRIPNULL_SPIDERS')
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats, crawler.settings)

    def process_response(self, request, response, spider):
        if spider.name not in self.spiders:
            self.stats.inc_value('risjstripnull/skipped', spider=spider)
            return response

        newbody = bytes([x for x in response.body if x != 0])

        if len(newbody) < len(response.body):
            self.stats.inc_value('risjstripnull/stripped', spider=spider)
            return response.replace(body = newbody)
        else:
            self.stats.inc_value('risjstripnull/clean', spider=spider)
            return response

