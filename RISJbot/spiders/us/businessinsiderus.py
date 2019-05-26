# -*- coding: utf-8 -*-
from RISJbot.spiders.base.businessinsiderspider import BusinessInsiderSpider

# NOTE: Inherits parsing code etc. overriding only the name and start URL.
class BusinessInsiderUSSpider(BusinessInsiderSpider):
    name = 'businessinsiderus'
    # allowed_domains = ['www.businessinsider.com']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['https://www.businessinsider.com/sitemap/google-news.xml'] 

    def parse_page(self, response):
        """@url http://www.businessinsider.com/ainsley-earhardt-rising-star-fox-friends-who-is-profile-2017-9?IR=C
        @returns items 1
        @scrapes bodytext bylines fetchtime modtime headline
        @scrapes keywords section source summary url language
        @noscrapes firstpubtime
        """
        return super().parse_page(response)

