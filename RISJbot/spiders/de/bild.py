# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from RISJbot.spiders.newsspecifiedspider import NewsSpecifiedSpider
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del
from scrapy.linkextractors import LinkExtractor
from itemloaders.processors import Identity, TakeFirst
from itemloaders.processors import Join, Compose, MapCompose

class BildParser(object):
    def parse_page(self, response):
        """@url https://www.bild.de/politik/ausland/politik-ausland/wef-in-davos-die-top-gaeste-und-die-wichtigsten-themen-67441554.bild.html
        @returns items 1
        @scrapes bodytext bylines fetchtime firstpubtime modtime headline
        @scrapes keywords section source summary url language
        """
        
        s = response.selector

        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.
        # Drop noscript JS warnings (which are otherwise included as the
        # bodytext for video pages).
        mutate_selector_del(s, 'xpath', '//noscript[contains(@class, "warning")]')
        # Remove BildPLUS subscribe notice (note that BildPLUS articles are
        # paywalled, and the text fetched will be only the opening paragraphs.
        mutate_selector_del(s, 'xpath', '//strong[text()="Ihre neuesten Erkenntnisse lesen Sie mit BILDplus."]')
        # Remove "related topics" etc.
        mutate_selector_del(s, 'xpath', '//aside[contains(@class, "related-topics")]')
        mutate_selector_del(s, 'xpath', '//div[contains(@class, "tsr-info") and contains(text(), "Lesen Sie auch")]')

        l = NewsLoader(selector=s)

        # Breadcrumbs section
        l.add_xpath('section', '//div[@id="breadcrumb"]//a[@rel="home"]//text()')
        
        # Add a number of items of data that should be standardised across
        # providers. Can override these (for TakeFirst() fields) by making
        # l.add_* calls above this line, or supplement gaps by making them
        # below.
        l.add_fromresponse(response)
        l.add_htmlmeta()
        l.add_schemaorg(response)
        l.add_opengraph()
        l.add_scrapymeta(response)
        l.add_readability(response)
        #l.add_schemaorg_bylines()
        #l.add_dublincore()

        # Readability is pretty good on Bild, but sometimes misses the body.
        # Try fallback (this won't be as clean as the readability version as
        # we haven't removed all the "more reading" sections etc.)
        l.add_xpath('bodytext', '//div[contains(@class, "txt")]//text()')
        l.add_xpath('bodytext', '//div[contains(@class, "article-body")]//text()')
        # Dates are a bit tricky. They aren't consistently tagged in the
        # article body, and the JSONld block isn't always well-formed JSON
        # (which stops extraction from the metadata block).
        # The dates in the block at the top of the article are firstpubtimes,
        # not modtimes, although not labelled as such.
        l.add_xpath('firstpubtime', '//time[contains(@class, "authors__pubdate")]/@datetime')
        l.add_xpath('firstpubtime', '//div[contains(@class, "article")]/div[contains(@class, "date")]/time[@datetime]/@datetime')
        l.add_xpath('firstpubtime', '//div[contains(@class, "content")]//time[contains(@class, "date")]/@datetime')

        return l.load_item()

class BildSpider(BildParser, CrawlSpider):
    """This crawler scrapes from bild.de by using its published daily archive.
       By default it fetches only today's published articles, but there is a
       commented LinkExtractor rule to fetch the full archive if desired."""
    name = 'bild'
    allowed_domains = ['www.bild.de']
    start_urls = ['https://www.bild.de/archive/index.html']

    rules = (
        # Follow links to other archive pages - specifically allowing us to
        # get pages from previous days
#        Rule(LinkExtractor(allow=r'/archive/[0-9]+/[0-9]+/[0-9]+/index\.html'),
#             callback='parse',
#             follow=True),
        # Fetch the actual articles.
        # Most of the exclusion items live in the header. We also try to select
        # only the relevant body items using the '//p' xpath.
        Rule(LinkExtractor(deny=[r'/(archive|faq|corporate-site)/*',
                                 r'/politik/ombudsmann/bild-ombudsmann/ernst-elitz-51709536\.bild\.html',
                                 r'/news/bild-kaempft/bild-kaempft-fuer-sie/bild-kaempft-43942532.bild.html'],
                           restrict_xpaths='//p'),
             callback='parse_page',
             follow=False),
    )


class BildSpecifiedSpider(BildParser, NewsSpecifiedSpider):
    name = "bildspecified"

