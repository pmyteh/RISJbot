# -*- coding: utf-8 -*-
import logging
from scrapy.spiders import XMLFeedSpider
from scrapy.http import Request

logger = logging.getLogger(__name__)

class NewsAtomFeedSpider(XMLFeedSpider):
    iterator = 'iternodes' # you can change this; see the docs
    itertag = 'entry' # change it accordingly

    def parse_node(self, response, selector):
        for url in selector.xpath('link/@href').extract():
            yield self.url_to_request(url, meta={'originalurl': url})

    def parse_page(self, response):
        raise NotImplementedError

    def url_to_request(self, url, callback=None, meta={}):
        if callback is None:
            callback = self.parse_page
        return Request(url.strip(), callback=callback, meta=meta)

