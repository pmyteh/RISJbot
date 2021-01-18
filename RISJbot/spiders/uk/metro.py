# -*- coding: utf-8 -*-
from RISJbot.spiders.newssitemapspider import NewsSitemapSpider
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del_xpath
from itemloaders.processors import Identity, TakeFirst
from itemloaders.processors import Join, Compose, MapCompose
import re

class MetroSpider(NewsSitemapSpider):
    name = 'metro'
    # allowed_domains = ['metro.co.uk']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://metro.co.uk/news-sitemap.xml'] 

    def parse_page(self, response):
        """@url http://metro.co.uk/2017/02/22/telescope-spots-our-best-bet-for-finding-aliens-a-nearby-star-with-seven-earth-sized-planets-6464648/
        @returns items 1
        @scrapes bodytext bylines fetchtime firstpubtime modtime headline
        @scrapes keywords section source summary url
        """
        s = response.selector
        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.        
        #mutate_selector_del_xpath(s, '//*[@style="display:none"]')

        l = NewsLoader(selector=s)

        # articleBody full of headline/byline/fluff
        l.add_xpath('bodytext', '//div[contains(@class, "article-body")]//text()')


        # Add a number of items of data that should be standardised across
        # providers. Can override these (for TakeFirst() fields) by making
        # l.add_* calls above this line, or supplement gaps by making them
        # below.
        l.add_fromresponse(response)
        l.add_htmlmeta()
        l.add_schemaorg(response)
        l.add_opengraph()
        l.add_scrapymeta(response)

        # Sort out bylines with less fluff
        l.add_xpath('bylines', '//span[contains(@class, "byline")]//a[@rel="author"]//text()', MapCompose(lambda s: re.sub(r' For Metro\.co\.uk', r'', s, flags=re.IGNORECASE)))

        return l.load_item()
