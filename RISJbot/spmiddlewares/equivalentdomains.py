# -*- coding: utf-8 -*-

import logging
import urllib
from scrapy.http import Request
from scrapy.item import BaseItem
from scrapy.exceptions import NotConfigured

logger = logging.getLogger(__name__)

class EquivalentDomains(object):
    """Spider middleware to coerce sets of equivalent domains to a single
       canonical location. This can deal with situations like
       editions.cnn.com and www.cnn.com, which deliver identical content.
       Should be put early in the chain.

       EQUIVALENTDOMAINS_MAPPINGS is a dict of substitutions
       {domaintoreplace: newdomain}
    """

    def __init__(self, stats, settings):
        if not settings.getbool('EQUIVALENTDOMAINS_ENABLED'):
            raise NotConfigured
        self.mappings = settings.get('EQUIVALENTDOMAINS_MAPPINGS')
        self.stats = stats
        logger.debug("EquivalentDomains starting; mappings: "
                        "{}".format(self.mappings))

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats, crawler.settings)

    def process_spider_output(self, response, result, spider):
        return (self.process_item(r, spider) for r in result)

    def process_item(self, o, spider):
        if isinstance(o, Request):
            # Get the domain name (actually domain:port if given)
            u = urllib.parse.urlparse(o.url)
            # Are we munging this domain?
            if u.netloc in self.mappings:
                # Regenerate the URL using the new domain
                newurl = urllib.parse.urlunparse([u.scheme,
                                                  self.mappings[u.netloc],
                                                  u.path,
                                                  u.params,
                                                  u.query,
                                                  u.fragment])
                logger.debug('Replacing {} with {}'.format(o.url, newurl))
                self.stats.inc_value('equivalentdomains/munged', spider=spider)
                o = o.replace(url=newurl)
        return o

