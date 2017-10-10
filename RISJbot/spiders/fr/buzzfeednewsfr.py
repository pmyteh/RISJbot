# -*- coding: utf-8 -*-
from RISJbot.spiders.base.buzzfeednewscrawlspider import BuzzfeedNewsCrawlSpider

# NOTE: Inherits parsing code etc., overriding only the name and start URL.
class BuzzfeedNewsFRSpider(BuzzfeedNewsCrawlSpider):
    name = 'buzzfeednewsfr'
    start_urls = ['https://www.buzzfeed.com/news?country=fr-fr']

    def parse_page(self, response):
        """@url https://www.buzzfeed.com/davidperrotin/la-patronne-de-free-epinglee-par-cash-investigation-decoree
        @returns items 1
        @scrapes bodytext bylines fetchtime headline modtime
        @scrapes section source summary url keywords
        @noscrapes firstpubtime
        """
        return super().parse_page(response)

