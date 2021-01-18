# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del_xpath
from scrapy.linkextractors import LinkExtractor
from itemloaders.processors import Identity, TakeFirst
from itemloaders.processors import Join, Compose, MapCompose
import re

class APSpider(CrawlSpider):
    """UPDATE: bigstory.ap.org is defunct; a new crawler could be written
       for https://apnews.com/, which seems to have a suitable sitemap.
       Until that happens, APSpider is non-functional.

       APSpider crawls the Associated Press.

       AP is a difficult beast to crawl; it has at least three different
       expressions of content on its own site (hosted.ap.org, hosted2.ap.org,
       and bigstory.ap.org), quite apart from the feeds it gives to its
       members, and apnews.com which seems US-focused.

       None of these three sites have Google News sitemaps. hosted
       has a series of RSS feeds (both advertised and unadvertised*), hosted2
       has a series of (5 item) Atom feeds. bigstory seems to have nothing.

       Unfortunately, bigstory has properly-annotated HTML content including
       metadata, while hosted does not, and hosted2 has been formally
       suspended. Bizarrely, hosted does get (some) metadata when it's
       reskinned into a partner's branding  - see
       http://hosted.ap.org/dynamic/stories/U/US_WOMENS_DAY_WIOL-?SITE=MOCOD&SECTION=HOME&TEMPLATE=DEFAULT&CTIME=2017-03-08-07-47-16 

       This leaves two options: scrape bigstory.ap.org using a CrawlSpider,
       but enjoy OG metadata etc., or use the hosted.ap.org RSS feed and
       extract all the content from the page by hand. This is somewhat more
       fragile, so we do the former.

       WARNING: bigstory.ap.org/latest (and possibly other pages from the site)
                have embedded ASCII NUL bytes in them, which really mess up
                the lxml parser used by Scrapy. The RISJStripNull downloader
                middleware is needed to strip these for this spider to
                function properly.

      *: Should you decide to RSS crawl hosted.ap.org, the unadvertised 'raw'
         feed is at http://hosted.ap.org/lineups/RAWHEADS.rss
    """

"""
    name = 'ap'
    allowed_domains = ['bigstory.ap.org']
    start_urls = ['http://bigstory.ap.org/latest']

    rules = (Rule(LinkExtractor(allow='/article/'),
                  callback='parse_page',
                  follow=False),
            )

    def parse_page(self, response):
"""        """@url http://bigstory.ap.org/article/fc451fdf7e9a47c1b2b9ab95f55c3bfe/tusk-closing-2nd-term-eu-council-president
        @returns items 1
        @scrapes bodytext bylines fetchtime modtime headline
        @scrapes keywords source summary url
        @noscrapes firstpubtime section
        """
"""
        s = response.selector
        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.        
        #mutate_selector_del_xpath(s, '//*[contains(@class, "classname")]')

        l = NewsLoader(selector=s)

        l.add_value('source', 'Associated Press')

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

        l.add_xpath('headline', 'head/title/text()')
        l.add_xpath('summary', 'head/meta[@name="description"]/@content')
        l.add_xpath('bylines', '//div[@id="byline"]//a/text()')
        l.add_xpath('bodytext', '//div[contains(@class, "field-name-body")]//text()')
        l.add_xpath('modtime', '//div[@id="dateline"]/span[contains(@class, "updated")]/@title')
        # These are sometimes exposed as <meta name='keywords'>, sometimes not.
        l.add_xpath('keywords', '//div[contains(@class, "tags")]//a/text()')

        return l.load_item()
"""
