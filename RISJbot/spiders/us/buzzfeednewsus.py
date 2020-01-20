# -*- coding: utf-8 -*-
from RISJbot.spiders.base.buzzfeednewscrawlspider import BuzzfeedNewsCrawlSpider

# NOTE: Inherits parsing code etc., overriding only the name and start URL.
class BuzzfeedNewsUSSpider(BuzzfeedNewsCrawlSpider):
    name = 'buzzfeednewsus'
    start_urls = ['https://www.buzzfeednews.com/sitemap/recent/en-us.xml']

    def parse_page(self, response):
        """@url https://www.buzzfeednews.com/article/maryanngeorgantopoulos/white-supremacists-are-spreading-their-message-on-college-ca
        @returns items 1
        @scrapes bodytext bylines fetchtime headline modtime
        @scrapes section source summary url keywords
        @noscrapes firstpubtime
        """
        return super().parse_page(response)

