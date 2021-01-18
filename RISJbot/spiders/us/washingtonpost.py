# -*- coding: utf-8 -*-
from RISJbot.spiders.newssitemapspider import NewsSitemapSpider
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del_xpath
from itemloaders.processors import Identity, TakeFirst
from itemloaders.processors import Join, Compose, MapCompose
import re

class WashingtonPostSpider(NewsSitemapSpider):
    name = 'washingtonpost'
    # allowed_domains = ['washingtonpost.com']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['https://www.washingtonpost.com/news-sitemaps/index.xml']

    def parse_page(self, response):
        """@url https://www.washingtonpost.com/news/politics/wp/2017/03/27/trumps-approval-hits-a-new-low-of-36-percent-but-thats-not-the-bad-news/
        @returns items 1
        @scrapes bodytext bylines fetchtime firstpubtime headline
        @scrapes keywords section source summary url
        @noscrapes modtime
        """
        s = response.selector
        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.        
        #mutate_selector_del_xpath(s, '//*[@style="display:none"]')

        l = NewsLoader(selector=s)

        # WaPo's ISO date/time strings are invalid: <datetime>-500 instead of
        # <datetime>-05:00. Note that the various standardised l.add_* methods
        # will generate 'Failed to parse data' log items. We've got it properly
        # here, so they aren't important.
        l.add_xpath('firstpubtime',
                    '//*[@itemprop="datePublished" or '
                        '@property="datePublished"]/@content',
                    MapCompose(self.fix_iso_date)) # CreativeWork

        # These are duplicated in the markup, so uniquise them.
        l.add_xpath('bylines',
                    '//*[@itemprop="author"]//*[@itemprop="name"]//text()',
                    set)
        l.add_xpath('section',
                    '//*[contains(@class, "headline-kicker")]//text()')


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

    def fix_iso_date(self, s):
        return re.sub(r'^([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}[+-])'
                            '([0-9])([0-9]{2})$',
                      r'\g<1>0\g<2>:\g<3>',
                      s)

