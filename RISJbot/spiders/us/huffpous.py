# -*- coding: utf-8 -*-
from RISJbot.spiders.base.huffpospider import HuffPoSpider

# NOTE: Inherits parsing code etc., overriding only the name and start URL.
class HuffPoUSSpider(HuffPoSpider):
    name = 'huffpous'
    # allowed_domains = ['www.huffingtonpost.com']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://www.huffingtonpost.com/sitemaps/sitemap-google-news.xml']

    # Dodgy gzip encoding on http://www.huffingtonpost.com/robots.txt
    custom_settings = {'COMPRESSION_ENABLED': False}

    def parse_page(self, response):
        """@url http://www.huffingtonpost.com/entry/trump-obamacare-executive-action_us_59daa131e4b046f5ad9923a9
        @returns items 1
        @scrapes bodytext bylines fetchtime firstpubtime modtime headline
        @scrapes keywords section source summary url
        """
        return super().parse_page(response)


