# -*- coding: utf-8 -*-
from RISJbot.spiders.newssitemapspider import NewsSitemapSpider
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del_xpath
from itemloaders.processors import Identity, TakeFirst
from itemloaders.processors import Join, Compose, MapCompose
import re

class AbcSpider(NewsSitemapSpider):
    name = 'abc'
    # allowed_domains = ['abcnews.go.com']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://abcnews.go.com/xmlLatestStories'] 

    def parse_page(self, response):
        """@url http://abcnews.go.com/Politics/house-intelligence-committee-sets-framework-russian-probe/story?id=45846073
        @returns items 1
        @scrapes bodytext bylines fetchtime firstpubtime modtime headline
        @scrapes keywords section source summary url
        """
        s = response.selector
        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.        
        #mutate_selector_del_xpath(s, '//*[@style="display:none"]')

        l = NewsLoader(selector=s)

        # Add a number of items of data that should be standardised across
        # providers. Can override these (for TakeFirst() fields) by making
        # l.add_* calls above this line, or supplement gaps by making them
        # below.
        l.add_fromresponse(response)
        l.add_htmlmeta()
        l.add_schemaorg(response)
        l.add_opengraph()
        l.add_scrapymeta(response)

        l.add_xpath('section', '//article/@data-section')
        l.add_xpath('modtime', 'head/meta[@name="Last-Modified"]/@content')
        l.add_xpath('firstpubtime', '//div[contains(@class, "article-meta")]//span[contains(@class, "timestamp")]/text()', self._strip_timestamp)

        return l.load_item()

    @staticmethod
    def _strip_timestamp(ts):
        try:
            return re.sub(r'.* — ', '', ts, count=1)
        except TypeError:
            return ts
