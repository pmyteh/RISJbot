# -*- coding: utf-8 -*-
from RISJbot.spiders.newsrssfeedspider import NewsRSSFeedSpider
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del_xpath
from itemloaders.processors import Identity, TakeFirst
from itemloaders.processors import Join, Compose, MapCompose

class SunSpider(NewsRSSFeedSpider):
    name = 'sun'
    # allowed_domains = ['thesun.co.uk']
    start_urls = ['https://www.thesun.co.uk/feed/']

    # RSSFeedSpider parses the RSS feed and calls parse_page(response) as a
    # callback for each page it finds in the feed.
    def parse_page(self, response):
        """@url https://www.thesun.co.uk/living/2937147/human-ken-doll-quentin-dehar-who-spent-92k-to-look-like-his-idol-has-dumped-his-surgery-obsessed-barbie-girlfriend-for-dying-her-hair-brown/
        @returns items 1
        @scrapes bodytext bylines fetchtime firstpubtime modtime headline
        @scrapes keywords section source summary url
        """

        s = response.selector
        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.

        # TODO: 'Keywords' and 'tags' for The Sun are different. Decide which
        #       which we want.

        # Lose "The Sun" link on the bottom of each page  
        mutate_selector_del_xpath(s, '//div[contains(@class, "social--fb-page-button")]')
        # Lose the "related articles" carousel        
        mutate_selector_del_xpath(s, '//div[contains(@class, "rail--trending")]')

        l = NewsLoader(selector=s)

        l.add_xpath('summary', 'meta[@name="description"]/@content')

        # TODO: This is kinda grot. Fine except for names like "John da Silva".
        l.add_xpath('bylines', '//span[contains(@class, "article__author-name")]//text()', lambda x: (s.title() for s in x))

        # Add a number of items of data that should be standardised across
        # providers. Can override these (for TakeFirst() fields) by making
        # l.add_* calls above this line, or supplement gaps by making them
        # below.
        l.add_fromresponse(response)
        l.add_htmlmeta()
        l.add_schemaorg(response)
        l.add_opengraph()
        l.add_scrapymeta(response)

        l.add_xpath('bodytext', '//article//div[contains(@class, "article__content")]//text()')

        return l.load_item()
