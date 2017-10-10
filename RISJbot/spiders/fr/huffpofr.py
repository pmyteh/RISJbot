# -*- coding: utf-8 -*-
from RISJbot.spiders.base.huffpospider import HuffPoSpider

# NOTE: Inherits parsing code etc., overriding only the name and start URL.
class HuffPoFRSpider(HuffPoSpider):
    name = 'huffpofr'
    # allowed_domains = ['www.huffingtonpost.fr']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://www.huffingtonpost.fr/custom-sitemaps/original-content-map.xml'] 

    def parse_page(self, response):
        """@url http://www.huffingtonpost.fr/2017/10/08/furieux-de-voir-le-fn-debarquer-dans-son-village-un-maire-propose-sa-demission_a_23236402/
        @returns items 1
        @scrapes bodytext bylines fetchtime firstpubtime modtime headline
        @scrapes keywords section source summary url
        """
        return super().parse_page(response)

