# -*- coding: utf-8 -*-
from RISJbot.spiders.base.vicespider import ViceSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

# NOTE: Inherits parsing code etc., overriding only the name and start URL.
class ViceDESpider(ViceSpider):
    name = 'vicede'
    start_urls = ['https://www.vice.com/de/latest',
                  'https://www.vice.com/de/latest?page=2']

    rules = (
        Rule(LinkExtractor(allow=r'/de/article/|/story/'),
             callback='parse_page'),
    )

    def parse_page(self, response):
        """@url https://www.vice.com/de/article/3kawx8/g20-cdu-will-dass-studenten-sich-gegenseitig-bespitzeln
        @returns items 1
        @scrapes fetchtime firstpubtime headline
        @scrapes keywords source summary url language
        @noscrapes modtime bodytext bylines
        @noscrapes section
        """
        # bodytext and bylines also fetched, but only via Splash
        # (which scrapy check does not do)
        return super().parse_page(response)

