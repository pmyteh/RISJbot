# -*- coding: utf-8 -*-
from RISJbot.spiders.base.huffpospider import HuffPoSpider

# NOTE: Inherits parsing code etc., overriding only the name and start URL.
class HuffPoDESpider(HuffPoSpider):
    name = 'huffpode'
    # allowed_domains = ['www.huffingtonpost.de']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://www.huffingtonpost.de/original-content-map.xml'] 

    def parse_page(self, response):
        """@url http://www.huffingtonpost.de/2017/10/09/schwiegertochter-gesucht-_n_18222232.html
        @returns items 1
        @scrapes bodytext bylines fetchtime firstpubtime modtime headline
        @scrapes keywords section source summary url
        """
        return super().parse_page(response)
