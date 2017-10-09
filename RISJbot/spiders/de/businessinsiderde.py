# -*- coding: utf-8 -*-
from RISJbot.spiders.us.businessinsiderus import BusinessInsiderUSSpider

# NOTE: Inherits parsing code etc. overriding only the name and start URL.
class BusinessInsiderDESpider(BusinessInsiderUSSpider):
    name = 'businessinsiderde'
    # allowed_domains = ['www.businessinsider.de']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://www.businessinsider.de/sitemap?map=news&IR=C'] 

