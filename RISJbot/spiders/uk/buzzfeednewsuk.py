# -*- coding: utf-8 -*-
from RISJbot.spiders.base.buzzfeednewscrawlspider import BuzzfeedNewsCrawlSpider

# NOTE: Inherits parsing code etc., overriding only the name and start URL.
class BuzzfeedNewsUKSpider(BuzzfeedNewsCrawlSpider):
    name = 'buzzfeednewsuk'
    start_urls = ['https://www.buzzfeed.com/news?country=en-uk']

    def parse_page(self, response):
        """@url https://www.buzzfeed.com/jamieross/nicola-sturgeon-has-criticised-the-eu-for-its-silence-over
        @returns items 1
        @scrapes bodytext bylines fetchtime headline modtime
        @scrapes section source summary url keywords
        @noscrapes firstpubtime
        """
        return super().parse_page(response)

