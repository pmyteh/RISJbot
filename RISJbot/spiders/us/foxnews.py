# -*- coding: utf-8 -*-
from RISJbot.spiders.newssitemapspider import NewsSitemapSpider
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del_xpath
from scrapy.loader.processors import Identity, TakeFirst
from scrapy.loader.processors import Join, Compose, MapCompose

class FoxNewsSpider(NewsSitemapSpider):
    name = 'foxnews'
    # allowed_domains = ['foxnews.com']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['http://www.foxnews.com/google_news_entertainment.xml',
                    'http://www.foxnews.com/google_news_opinion.xml', 
                    'http://www.foxnews.com/google_news_politics.xml',
                    'http://www.foxnews.com/google_news_science.xml',
                    'http://www.foxnews.com/google_news_tech.xml',
                    'http://www.foxnews.com/google_news_sports.xml',
                    'http://www.foxnews.com/google_news_weather.xml',
                    'http://www.foxnews.com/google_news_leisure.xml',
                    'http://www.foxnews.com/google_news_us.xml',
                    'http://www.foxnews.com/google_news_world.xml',
                    'http://www.foxnews.com/google_news_health.xml',
                    'http://www.foxnews.com/google_news_travel.xml',
                   ] 

    def parse_page(self, response):
        """@url http://www.foxnews.com/opinion/2017/02/28/if-trump-really-wants-to-restore-america-to-greatness-hell-have-to-compromise-with-democrats.html
        @returns items 1
        @scrapes bodytext bylines fetchtime firstpubtime modtime headline
        @scrapes section source summary url
        @noscrapes keywords
        """
        s = response.selector
        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.        
        #mutate_selector_del_xpath(s, '//*[@style="display:none"]')

        l = NewsLoader(selector=s)

        l.add_xpath('bodytext', '//*[contains(@class, "article-text")]//text()')
        l.add_xpath('section', '//*[contains(@class, "section-title")]//text()')
        l.add_xpath('section', 'head/meta[@name="prism-section"]/@content')
        # Well, this is awkward. Bylines (normally) not in metadata, and not
        # given a suitable class label in the HTML source.
        l.add_xpath('bylines', '//div[contains(@class, "article-info")]//p[contains(., "By")]/span//text()')

        # Add a number of items of data that should be standardised across
        # providers. Can override these (for TakeFirst() fields) by making
        # l.add_* calls above this line, or supplement gaps by making them
        # below.
        l.add_fromresponse(response)
        l.add_htmlmeta()
        l.add_dublincore()
        l.add_schemaorg(response)
        l.add_opengraph()
        l.add_scrapymeta(response)

        return l.load_item()
