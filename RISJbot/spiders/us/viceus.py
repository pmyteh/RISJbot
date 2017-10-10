# -*- coding: utf-8 -*-
from RISJbot.spiders.base.vicespider import ViceSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

# NOTE: Inherits parsing code etc., overriding only the name and start URL.
class ViceUSSpider(ViceSpider):
    name = 'viceus'
    start_urls = ['https://www.vice.com/en_us/latest']

    rules = (
        Rule(LinkExtractor(allow=r'/en_us/article/|/story/'),
             callback='parse_page'),
    )

    def parse_page(self, response):
        """@url https://www.vice.com/en_us/article/zm3qm9/hugh-hefner-has-died
        @returns items 1
        @scrapes bodytext fetchtime firstpubtime headline bylines
        @scrapes keywords source summary url language
        @noscrapes modtime
        @noscrapes section
        """
        return super().parse_page(response)

