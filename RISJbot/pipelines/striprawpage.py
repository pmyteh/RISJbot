# -*- coding: utf-8 -*-
import logging
from scrapy.exceptions import NotConfigured

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

logger = logging.getLogger(__name__)

class StripRawPage(object):
    """RISJbot is configured to store a Base64-encoded gzipped version of the
    raw Response in its JSON output by default. This pipeline class removes
    it when needed (for various reasons)."""
    def __init__(self, enabled=False):
        if not enabled:
            raise NotConfigured
        logger.debug("Stripping raw pages.")

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings.getbool('STRIPRAWPAGE_ENABLED'))

    def process_item(self, item, spider):
        try:
            del(item['rawpagegzipb64'])
        except KeyError:
            pass
        return item
