# -*- coding: utf-8 -*-
from RISJbot.spiders.us.buzzfeed import BuzzfeedSpider

# NOTE: Inherits parsing code etc. from spiders/us/buzzfeed, overriding only
#       the name and start URL.
class BuzzfeedUKSpider(BuzzfeedSpider):
    name = 'buzzfeeduk'
    # allowed_domains = ['buzzfeed.com']
    start_urls = ['https://www.buzzfeed.com/news.xml?country=uk']

