# -*- coding: utf-8 -*-
from RISJbot.spiders.newssitemapspider import NewsSitemapSpider
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del_xpath
from itemloaders.processors import Identity, TakeFirst
from itemloaders.processors import Join, Compose, MapCompose

class PRNewswireSpider(NewsSitemapSpider):
    name = 'prnewswire'
    # allowed_domains = ['prnewswire.com']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://www.prnewswire.com/sitemap-news.xml'] 

    def parse_page(self, response):
        """@url http://www.prnewswire.com/news-releases/xti-aircraft-company-and-bye-aerospace-form-alliance-on-hybridelectric-vertical-takeoff-airplane-300418161.html
        @returns items 1
        @scrapes bodytext bylines fetchtime firstpubtime headline
        @scrapes keywords source summary url
        @noscrapes modtime section
        """
        s = response.selector
        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.        
        #mutate_selector_del_xpath(s, '//*[contains(@class, "classname")]')

        l = NewsLoader(selector=s)

        l.add_value('source', 'PR Newswire')
        # Not parsing as head/meta for some reason
        l.add_xpath('summary', '//meta[@name="description"]/@content')
        l.add_xpath('bylines', '//meta[@name="author"]/@content')

        # Add a number of items of data that should be standardised across
        # providers. Can override these (for TakeFirst() fields) by making
        # l.add_* calls above this line, or supplement gaps by making them
        # below.
        l.add_fromresponse(response)
        l.add_htmlmeta()
        l.add_schemaorg(response)
        l.add_opengraph()
        l.add_scrapymeta(response)
        #l.add_schemaorg_bylines()
        #l.add_dublincore()

        l.add_xpath('firstpubtime', '//meta[@name="date"]/@content')


        return l.load_item()
