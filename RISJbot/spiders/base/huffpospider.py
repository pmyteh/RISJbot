# -*- coding: utf-8 -*-
from RISJbot.spiders.newssitemapspider import NewsSitemapSpider
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del_xpath
from itemloaders.processors import Identity, TakeFirst
from itemloaders.processors import Join, Compose, MapCompose

class HuffPoSpider(NewsSitemapSpider):
    def parse_page(self, response):
        s = response.selector
        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.        
        #mutate_selector_del_xpath(s, '//*[@style="display:none"]')

        l = NewsLoader(selector=s)

        l.add_xpath('bylines', '//*[contains(@class, "author-card__details__name")]//text()')
        # UK
        l.add_xpath('bodytext', '//div[contains(@class, "entry__body")]//text()')
        # DE
        l.add_xpath('bodytext', '//div[@id="mainentrycontent"]//text()')

        # Add a number of items of data that should be standardised across
        # providers. Can override these (for TakeFirst() fields) by making
        # l.add_* calls above this line, or supplement gaps by making them
        # below.
        l.add_fromresponse(response)
        l.add_htmlmeta()
        l.add_schemaorg(response)
        l.add_opengraph()
        l.add_scrapymeta(response)

        return l.load_item()
