# -*- coding: utf-8 -*-
from RISJbot.spiders.newssitemapspider import NewsSitemapSpider
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del_xpath
from itemloaders.processors import Identity, TakeFirst
from itemloaders.processors import Join, Compose, MapCompose
import re

class USATodaySpider(NewsSitemapSpider):
    name = 'usatoday'
    # Some of the links in the news_sitemap_index go to USA Today properties
    # away from usatoday.com. For consistency, we exclude these.
    allowed_domains = ['usatoday.com']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.

    sitemap_urls = ['https://www.usatoday.com/news-sitemap.xml'] 

    def parse_page(self, response):
        """@url http://www.usatoday.com/story/money/markets/2017/02/28/bonds-telling-less-bullish-tale-than-stocks/98503646/
        @returns items 1
        @scrapes bodytext bylines fetchtime firstpubtime modtime headline
        @scrapes keywords section source summary url
        """
        s = response.selector
        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.        
        mutate_selector_del_xpath(s, '//*[contains(@class, "inline-share-tools")]')
        mutate_selector_del_xpath(s, '//*[contains(@class, "article-print-url")]')
        mutate_selector_del_xpath(s, '//aside')

        l = NewsLoader(selector=s)

        l.add_xpath('bylines', 'head/meta[@name="cXenseParse:author"]/@content')
        # Section metadata comes out as "news,world". For this, take "News".
        l.add_xpath('section',
                    'head/meta[@itemprop="articleSection"]/@content',
                     Compose(TakeFirst(),
                             lambda x: x.split(','),
                             TakeFirst(),
                             lambda x: x.title(),
                            )
                   )

        # Video pages
        l.add_xpath('summary', '//p[contains(@class, "vgm-video-description")]//text()')


        # USA Today provide timestamps to millisecond precision, in a format
        # which dateparser can't handle.
        l.add_xpath('firstpubtime', '//*[@itemprop="datePublished" or @property="datePublished"]/@content', MapCompose(self.fix_usatoday_date)) # CreativeWork
        l.add_xpath('modtime', '//*[@itemprop="dateModified" or @property="dateModified"]/@content', MapCompose(self.fix_usatoday_date)) # CreativeWork

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

    def fix_usatoday_date(self, s):
        # 2017-02-27T18:02:16.787Z -> 2017-02-27T18:02:16Z
        return re.sub(r'^([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})\.[0-9]+', r'\1', s)

