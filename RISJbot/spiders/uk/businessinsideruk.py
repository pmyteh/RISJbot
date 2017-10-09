# -*- coding: utf-8 -*-
from RISJbot.spiders.us.businessinsiderus import BusinessInsiderUSSpider

# NOTE: Inherits parsing code etc. from spiders/us/businessinsiderus,
#       overriding only the name and start URL.
class BusinessInsiderUKSpider(BusinessInsiderUSSpider):
    name = 'businessinsideruk'
    # allowed_domains = ['uk.businessinsider.com']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://uk.businessinsider.com/sitemap?map=google-news&IR=C'] 

