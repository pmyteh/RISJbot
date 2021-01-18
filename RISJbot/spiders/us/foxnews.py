# -*- coding: utf-8 -*-
from RISJbot.spiders.newssitemapspider import NewsSitemapSpider
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del_xpath
from itemloaders.processors import Identity, TakeFirst
from itemloaders.processors import Join, Compose, MapCompose

class FoxNewsSpider(NewsSitemapSpider):
    name = 'foxnews'
    # allowed_domains = ['foxnews.com']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['https://www.foxnews.com/sitemap.xml?type=news']

    def parse_page(self, response):
        """@url http://www.foxnews.com/opinion/2017/02/28/if-trump-really-wants-to-restore-america-to-greatness-hell-have-to-compromise-with-democrats.html
        @returns items 1
        @scrapes bodytext bylines fetchtime firstpubtime modtime headline
        @scrapes section source summary url
        @noscrapes keywords
        """
        s = response.selector
        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.        
        #mutate_selector_del_xpath(s, '//*[@style="display:none"]')

        l = NewsLoader(selector=s)

        l.add_xpath('bodytext', '//*[contains(@class, "article-text")]//text()')
        l.add_xpath('section', '//*[contains(@class, "section-title")]//text()')
        l.add_xpath('section', 'head/meta[@name="prism-section"]/@content')
        # Well, this is awkward. Bylines (normally) not in metadata, and not
        # given a suitable class label in the HTML source.
        l.add_xpath('bylines', '//div[contains(@class, "article-info")]//p[contains(., "By")]/span//text()')

        # Add a number of items of data that should be standardised across
        # providers. Can override these (for TakeFirst() fields) by making
        # l.add_* calls above this line, or supplement gaps by making them
        # below.
        l.add_fromresponse(response)
        l.add_htmlmeta()
        l.add_dublincore()
        l.add_schemaorg(response)
        l.add_opengraph()
        l.add_scrapymeta(response)

        return l.load_item()
