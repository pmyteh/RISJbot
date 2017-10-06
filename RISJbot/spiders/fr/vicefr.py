# -*- coding: utf-8 -*-
from RISJbot.spiders.us.viceus import ViceUSSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

# NOTE: Inherits parsing code etc., overriding only the name and start URL.
class ViceFRSpider(ViceUSSpider):
    name = 'vicefr'
    start_urls = ['https://www.vice.com/fr/latest']

    rules = (
        Rule(LinkExtractor(allow=r'/fr/article/|/story/'),
             callback='parse_page'),
    )
