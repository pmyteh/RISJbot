# -*- coding: utf-8 -*-
from RISJbot.spiders.newssitemapspider import NewsSitemapSpider
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del_xpath
from itemloaders.processors import Identity, TakeFirst
from itemloaders.processors import Join, Compose, MapCompose

class CnnSpider(NewsSitemapSpider):
    name = 'cnn'
    # allowed_domains = ['cnn.com']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://www.cnn.com/sitemaps/sitemap-news.xml'] 

    def parse_page(self, response):
        """@url http://edition.cnn.com/2017/03/01/politics/joe-biden-hunter-beau/index.html
        @returns items 1
        @scrapes bodytext bylines fetchtime firstpubtime modtime headline
        @scrapes keywords section source summary url
        """
        s = response.selector
        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.        
        mutate_selector_del_xpath(s, '//div[contains(@class, "read-more-button")]')
        mutate_selector_del_xpath(s, '//div[contains(@class, "el__embedded")]')
        mutate_selector_del_xpath(s, '//div[contains(@class, "owl-carousel")]')

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

        l.add_xpath('headline', '//article//meta[@itemprop="alternativeHeadline"]/@content')
        l.add_xpath('headline', '//h1[contains(@class, "headline")]/text()')

        return l.load_item()
