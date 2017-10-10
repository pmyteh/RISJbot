# -*- coding: utf-8 -*-
from RISJbot.spiders.base.vicespider import ViceSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

# NOTE: Inherits parsing code etc., overriding only the name and start URL.
class ViceFRSpider(ViceSpider):
    name = 'vicefr'
    start_urls = ['https://www.vice.com/fr/latest',
                  'https://www.vice.com/fr/latest?page=2']

    rules = (
        Rule(LinkExtractor(allow=r'/fr/article/|/story/'),
             callback='parse_page'),
    )

    def parse_page(self, response):
        """@url https://www.vice.com/fr/article/wjxa8b/filiere-immigration-clandestine-france-proces
        @returns items 1
        @scrapes fetchtime firstpubtime headline
        @scrapes keywords source summary url language
        @noscrapes modtime bodytext bylines
        @noscrapes section
        """
        # bodytext and bylines also fetched, but only via Splash
        # (which scrapy check does not do)
        return super().parse_page(response)

