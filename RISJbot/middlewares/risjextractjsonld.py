# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import logging
import json
from pprint import pformat
from scrapy.exceptions import NotConfigured


logger = logging.getLogger(__name__)

class RISJExtractJSONLD(object):
    """Spider middleware to extract JSON-LD blocks and save their data into the
       Response's meta tag. This stops them being squelched by <script>-killing
       code and makes them easier to extract from.
    """
    def __init__(self, stats, settings):
        if not settings.getbool('RISJEXTRACTJSONLD_ENABLED'):
            raise NotConfigured
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats, crawler.settings)

    def process_spider_input(self, response, spider):
        # Attempt to collect JSON-LD <script> blocks from the Response,
        # filing them in 
        # This can pick up initial (possibly gzipped) sitemap
        # Responses, before they have made it to the Spider and been decoded.
        # In any case, we don't want to edit sitemap files (or RSS for that
        # matter. Filter this strictly to non-sitemap objects.
        try:
            for blob in response.xpath('//script[@type="application/ld+json"]/text()').extract():
                if 'json-ld' not in response.meta:
                    response.meta['json-ld'] = []
                content = json.loads(blob)
                logger.debug('JSON-LD found: '+pformat(content))
                response.meta['json-ld'].append(content)
        except AttributeError:
            # No xpath: Not XML/HTML doc (perhaps a gzipped Sitemap)
            pass
        return None # Success


