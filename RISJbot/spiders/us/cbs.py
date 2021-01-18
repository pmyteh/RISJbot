# -*- coding: utf-8 -*-
from RISJbot.spiders.newssitemapspider import NewsSitemapSpider
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del_xpath
from itemloaders.processors import Identity, TakeFirst
from itemloaders.processors import Join, Compose, MapCompose

class CbsSpider(NewsSitemapSpider):
    name = 'cbs'
    # allowed_domains = ['cbsnews.com']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://www.cbsnews.com/xml-sitemap/index/news.xml'] 

    def parse_page(self, response):
        """@url http://www.cbsnews.com/news/iraqi-boy-trapped-in-mosul-for-years-finally-reunited-with-mother/
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
#        l.add_schemaorg_mde(response, jsonld=True, rdfa=False, microdata=False)
        l.add_schemaorg(response)
        l.add_opengraph()
        l.add_scrapymeta(response)

        # Media pages. NOTE: These can be multipage; this will only get the
        # first page's text.
        l.add_xpath('bodytext', '//div[contains(@class, "post")]//text()')
        l.add_xpath('bodytext', '//div[@itemid="#article-entry"]//text()')

        return l.load_item()
