# -*- coding: utf-8 -*-
from RISJbot.spiders.uk.huffpouk import HuffPoUKSpider

# NOTE: Inherits parsing code etc., overriding only the name and start URL.
class HuffPoUSSpider(HuffPoUKSpider):
    name = 'huffpous'
    # allowed_domains = ['www.huffingtonpost.com']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://www.huffingtonpost.com/sitemaps/sitemap-google-news.xml'] 

