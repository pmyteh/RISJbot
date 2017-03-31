# -*- coding: utf-8 -*-
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del_xpath
from RISJbot.spiders.basespiders import NewsRSSFeedSpider
from scrapy.loader.processors import Identity, TakeFirst
from scrapy.loader.processors import Join, Compose, MapCompose
import re

class BBCSpider(NewsRSSFeedSpider):
    name = 'bbc'
    # allowed_domains = ['bbc.co.uk']
    start_urls = ['http://feeds.bbci.co.uk/news/rss.xml?edition=uk']

    # RSSFeedSpider parses the RSS feed and calls parse_page(response) as a
    # callback for each page it finds in the feed.
    def parse_page(self, response):
        # firstpubtime from RSS feed, so won't appear for contract.
        """@url http://www.bbc.co.uk/news/uk-politics-39020260
        @returns items 1
        @scrapes bodytext fetchtime headline
        @scrapes section source summary url
        @noscrapes modtime keywords
        """
        s = response.selector
        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.        
        mutate_selector_del_xpath(s, '//*[@class="off-screen"]')

        l = NewsLoader(selector=s)


        l.add_value('source', 'BBC News')

        # BBC titles all have dross at the end, even the embedded ones.
        l.add_xpath('headline', 'head/title/text()', lambda x: [re.sub(r' - BBC (News(beat)?|Sport)$', '', x[0])])

        # TODO: Publishes data (including datePublished) as JSON+LD.
        # Need parser. Note that it doesn't seem complete: articleBody in
        # the JSON+LD feed seems to only contain the standfirst.

        # Add a number of items of data that should be standardised across
        # providers. Can override these (for TakeFirst() fields) by making
        # l.add_* calls above this line, or supplement gaps by making them
        # below.
        l.add_fromresponse(response)
        l.add_htmlmeta()
        l.add_schemaorg(response)
        l.add_opengraph()
        l.add_scrapymeta(response)

        l.add_xpath('bodytext', '//div[contains(@class, "main_article_text")]//text()') # Newsbeat
        l.add_xpath('bodytext', '//div[contains(@class, "map-body")]//text()') # media-asset-page

        match = re.match
        # Newsbeat seems to use a different CMS, which doesn't supply the
        # usual metadata (but which does publish bylines!)
        if response.xpath('//div[contains(@class, "newsbeatlogo")]'):
            l.add_value('section', 'Newsbeat')

#        def strip_by(strl):
#            for s in strl:
#                yield re.sub(r'.*[Bb]y (.*)', r'\1', s).strip()
        l.add_xpath('bylines', '//span[contains(@class, "byline__name")]/text()')#, strip_by) # lambda y: map(lambda x: re.sub(r'.*By (.*)', r'\1', x).strip(), y))
        l.add_xpath('bylines', '//p[contains(@class, "byline")]/text()')#, strip_by) # lambda y: map(lambda x: re.sub(r'.*By (.*)', r'\1', x).strip(), y)) # Newsbeat






        # TODO: Keywords (none?)

        return l.load_item()


