# -*- coding: utf-8 -*-
from RISJbot.spiders.uk.huffpouk import HuffPoUKSpider

# NOTE: Inherits parsing code etc., overriding only the name and start URL.
class HuffPoFRSpider(HuffPoUKSpider):
    name = 'huffpofr'
    # allowed_domains = ['www.huffingtonpost.fr']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://www.huffingtonpost.fr/custom-sitemaps/original-content-map.xml'] 

