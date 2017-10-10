# -*- coding: utf-8 -*-
from RISJbot.spiders.base.vicespider import ViceSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

# NOTE: Inherits parsing code etc., overriding only the name and start URL.
class ViceDESpider(ViceSpider):
    name = 'vicede'
    start_urls = ['https://www.vice.com/de/latest']

    rules = (
        Rule(LinkExtractor(allow=r'/de/article/|/story/'),
             callback='parse_page'),
    )

    def parse_page(self, response):
        """@url https://www.vice.com/de/article/3kawx8/g20-cdu-will-dass-studenten-sich-gegenseitig-bespitzeln
        @returns items 1
        @scrapes bodytext fetchtime firstpubtime headline bylines
        @scrapes keywords source summary url language
        @noscrapes modtime
        @noscrapes section
        """
        return super().parse_page(response)

