# -*- coding: utf-8 -*-
from RISJbot.spiders.us.viceus import ViceUSSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

# NOTE: Inherits parsing code etc., overriding only the name and start URL.
class ViceDESpider(ViceUSSpider):
    name = 'vicede'
    start_urls = ['https://www.vice.com/de/latest']

    rules = (
        Rule(LinkExtractor(allow=r'/de/article/|/story/'),
             callback='parse_page'),
    )
