# -*- coding: utf-8 -*-
from RISJbot.spiders.base.businessinsiderspider import BusinessInsiderSpider

# NOTE: Inherits parsing code etc. overriding only the name and start URL.
class BusinessInsiderDESpider(BusinessInsiderSpider):
    name = 'businessinsiderde'
    # allowed_domains = ['www.businessinsider.de']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://www.businessinsider.de/sitemap?map=news&IR=C'] 

    def parse_page(self, response):
        """@url http://www.businessinsider.de/cdu-und-csu-wollen-zuwanderung-von-maximal-200-000-fluechtlingen-5737380
        @returns items 1
        @scrapes bodytext bylines fetchtime modtime headline
        @scrapes keywords section source summary url language
        @noscrapes firstpubtime
        """
        return super().parse_page(response)

