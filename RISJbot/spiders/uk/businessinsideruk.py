# -*- coding: utf-8 -*-
from RISJbot.spiders.base.businessinsiderspider import BusinessInsiderSpider

# NOTE: Inherits parsing code etc. overriding only the name and start URL.
class BusinessInsiderUKSpider(BusinessInsiderSpider):
    name = 'businessinsideruk'
    # allowed_domains = ['uk.businessinsider.com']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://uk.businessinsider.com/sitemap?map=google-news&IR=C'] 

    def parse_page(self, response):
        """@url http://uk.businessinsider.com/tories-at-war-as-brexiteers-demand-may-sacks-hammond-2017-10
        @returns items 1
        @scrapes bodytext bylines fetchtime modtime headline
        @scrapes keywords section source summary url language
        @noscrapes firstpubtime
        """
        return super().parse_page(response)

