# -*- coding: utf-8 -*-
from RISJbot.spiders.newsrssfeedspider import NewsRSSFeedSpider
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del_xpath
from itemloaders.processors import Identity, TakeFirst
from itemloaders.processors import Join, Compose, MapCompose

class YahooSpider(NewsRSSFeedSpider):
    name = 'yahoo'
    # allowed_domains = ['yahoo.com']
    start_urls = ['https://www.yahoo.com/news/rss']

    # RSSFeedSpider parses the RSS feed and calls parse_page(response) as a
    # callback for each page it finds in the feed.
    def parse_page(self, response):
        """@url https://www.yahoo.com/news/school-principal-trump-chants-crossed-line-hate-speech-155230984.html
        @returns items 1
        @scrapes bodytext bylines fetchtime firstpubtime headline
        @scrapes source summary url keywords
        @noscrapes modtime section
        """
        # Depressing lack of modtime, keywords or section.

        s = response.selector
        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.        
        #mutate_selector_del_xpath(s, '//*[@style="display:none"]')

        l = NewsLoader(selector=s)

        l.add_value('source', 'Yahoo! News [US]')

        # Add a number of items of data that should be standardised across
        # providers. Can override these (for TakeFirst() fields) by making
        # l.add_* calls above this line, or supplement gaps by making them
        # below.
        l.add_fromresponse(response)
        l.add_htmlmeta()
#        l.add_schemaorg(response)
        l.add_opengraph()
        l.add_scrapymeta(response)

        l.add_xpath('bodytext', '//div[contains(@class, "canvas-body")]/p/text()')
        # NOTE: Maybe modtime
        l.add_xpath('firstpubtime', '//div[contains(@class, "auth-attr")]//time/@datetime')
        l.add_xpath('bylines',      '//div[contains(@class, "auth-attr")]//div[contains(@class, "author-name")]//text()')

        return l.load_item()
