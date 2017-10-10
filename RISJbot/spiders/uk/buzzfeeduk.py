# -*- coding: utf-8 -*-
from RISJbot.spiders.base.buzzfeedspider import BuzzfeedSpider

# NOTE: Inherits parsing code etc., overriding only the name and start URL.
class BuzzfeedUKSpider(BuzzfeedSpider):
    name = 'buzzfeeduk'
    # allowed_domains = ['buzzfeed.com']
    start_urls = ['https://www.buzzfeed.com/news.xml?country=uk']

    def parse_page(self, response):
        """Note: firstpubtime also fetched, but via RSS feed (which can't be
                 contracted for)

        @url https://www.buzzfeed.com/jamieross/this-scottish-politician-is-looking-for-your-support-on
        @returns items 1
        @scrapes bodytext bylines fetchtime headline
        @scrapes section source summary url keywords
        @noscrapes modtime
        """
        return super().parse_page(response)

