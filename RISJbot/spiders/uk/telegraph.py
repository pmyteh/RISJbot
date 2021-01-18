# -*- coding: utf-8 -*-
from RISJbot.spiders.newssitemapspider import NewsSitemapSpider
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del_xpath
from itemloaders.processors import Identity, TakeFirst
from itemloaders.processors import Join, Compose, MapCompose

class TelegraphSpider(NewsSitemapSpider):
    name = 'telegraph'
    # allowed_domains = ['telegraph.co.uk']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://www.telegraph.co.uk/sitemap-news.xml'] 

    def parse_page(self, response):
        """@url http://www.telegraph.co.uk/news/2017/02/27/grandmother-has-married-briton-27-years-deported-singapore-just/
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

        # This extracts the (top-level) section from the Navigation headline
        # bar. Probably a bit fragile.
        l.add_xpath('section', '//a[contains(@class, "header-breadcrumbs__link")]//text()', TakeFirst())

        l.add_xpath('bylines', '//main//*[@itemprop="author"]//*[@itemprop="name"]//text()')

        # Add a number of items of data that should be standardised across
        # providers. Can override these (for TakeFirst() fields) by making
        # l.add_* calls above this line, or supplement gaps by making them
        # below.
        l.add_fromresponse(response)
        l.add_htmlmeta()
        l.add_schemaorg(response)
        l.add_opengraph()
        l.add_scrapymeta(response)

        if response.xpath('//div[contains(@class, "premium-paywall")]'):
            l.add_value('notes', 'Premium paywall')

        return l.load_item()
