# -*- coding: utf-8 -*-
from RISJbot.spiders.newssitemapspider import NewsSitemapSpider
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del
from itemloaders.processors import Identity, TakeFirst
from itemloaders.processors import Join, Compose, MapCompose

class IndependentSpider(NewsSitemapSpider):
    name = 'independent'
    # Don't accept off-domain redirects to thinly-branded content from other
    # providers (Evening Standard, TheStreet.com etc.)
    allowed_domains = ['independent.co.uk']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://www.independent.co.uk/googlenewssitemap'] 

    def parse_page(self, response):
        """@url http://www.independent.co.uk/news/world/americas/muslim-american-activist-tarek-el-messidi-jewish-cemetery-mt-carmel-philadelphia-vandalised-a7601266.html
        @returns items 1
        @scrapes bodytext bylines fetchtime firstpubtime modtime headline
        @scrapes keywords section source summary url
        """
        s = response.selector
        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.

        # Picture galleries, generally unrelated to the story
        mutate_selector_del(s, 'css', '.type-gallery')
        # "More about" grot
        mutate_selector_del(s,
                            'xpath',
                            '//li[contains(text(), "More about")]/'
                                'parent::*[contains(@class, '
                                '"inline-pipes-list")]')

        l = NewsLoader(selector=s)

        l.add_xpath('bylines', '//article//*[@itemprop="author"]//*[@itemprop="name"]//text()')
        
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
