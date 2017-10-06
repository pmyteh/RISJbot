# -*- coding: utf-8 -*-
from RISJbot.spiders.us.viceus import ViceUSSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

# NOTE: Inherits parsing code etc., overriding only the name and start URL.
class ViceUKSpider(ViceUSSpider):
    name = 'viceuk'
    start_urls = ['https://www.vice.com/en_uk/latest']

    rules = (
        Rule(LinkExtractor(allow=r'/en_uk/article/|/story/'),
             callback='parse_page'),
    )
