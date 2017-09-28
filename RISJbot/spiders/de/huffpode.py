# -*- coding: utf-8 -*-
from RISJbot.spiders.uk.huffpouk import HuffPoUKSpider

# NOTE: Inherits parsing code etc., overriding only the name and start URL.
class HuffPoDESpider(HuffPoUKSpider):
    name = 'huffpode'
    # allowed_domains = ['www.huffingtonpost.de']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://www.huffingtonpost.de/original-content-map.xml'] 

