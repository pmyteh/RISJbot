# -*- coding: utf-8 -*-
import logging
from scrapy.spiders import XMLFeedSpider
from scrapy.http import Request
from RISJbot.utils import etree_to_recursive_dict

logger = logging.getLogger(__name__)

class NewsRSSFeedSpider(XMLFeedSpider):
    iterator = 'iternodes' # you can change this; see the docs
    itertag = 'item' # change it accordingly

    def parse_node(self, response, selector):
        nf = etree_to_recursive_dict(selector.root)[1]
        # Extract URL and submit Request for crawling
        url = selector.xpath('link/text()').extract_first()
        if url:
            meta = {'RSSFeed': nf, 'originalurl': url}
            yield self.url_to_request(url, meta=meta)
        else:
            self.logger.debug('No URL for %s' % str(selector.extract()))

    def parse_page(self, response):
        raise NotImplementedError

    def url_to_request(self, url, callback=None, meta={}):
        if callback is None:
            callback = self.parse_page
        return Request(url.strip(), callback=callback, meta=meta)

