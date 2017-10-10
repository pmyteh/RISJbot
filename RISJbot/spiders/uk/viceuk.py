# -*- coding: utf-8 -*-
from RISJbot.spiders.base.vicespider import ViceSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

# NOTE: Inherits parsing code etc., overriding only the name and start URL.
class ViceUKSpider(ViceSpider):
    name = 'viceuk'
    start_urls = ['https://www.vice.com/en_uk/latest']

    rules = (
        Rule(LinkExtractor(allow=r'/en_uk/article/|/story/'),
             callback='parse_page'),
    )

    def parse_page(self, response):
        """@url https://www.vice.com/en_uk/article/zm395y/will-rent-caps-in-scotland-offer-a-solution-to-the-housing-crisis
        @returns items 1
        @scrapes bodytext fetchtime firstpubtime headline bylines
        @scrapes keywords source summary url language
        @noscrapes modtime
        @noscrapes section
        """
        return super().parse_page(response)

