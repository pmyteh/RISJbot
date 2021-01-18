# -*- coding: utf-8 -*-
from RISJbot.spiders.newssitemapspider import NewsSitemapSpider
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del
from itemloaders.processors import Identity, TakeFirst
from itemloaders.processors import Join, Compose, MapCompose
import re
import datetime

def gen_reuters_recent_regex(days):
    now = datetime.datetime.now()
    # Sitemap URLs are like http://uk.reuters.com/sitemap_20170309-20170310.xml
    dates = [now - datetime.timedelta(days=n) for n in range(days+1)]
    s = '('
    for d in dates:
        s += '{:04d}{:02d}{:02d}|'.format(d.year, d.month, d.day)
    s = s[:-1] + r')\.xml$'
    return re.compile(s)

class ReutersSpider(NewsSitemapSpider):
    name = 'reuters'
    # allowed_domains = ['uk.reuters.com']
    # NOTE: This is a full sitemap, not the usual Google News feed. We use
    #       sitemap_follow to restrict this only to the last few days
    # FIXME: These don't seem to be published until quite early the following
    #        morning, in a batch. Perhaps move to RSS feeds? (Multiple, at
    #        http://uk.reuters.com/tools/rss). Note that these spray URLs which
    #        are (1) not unique for a given article - different URLs accessing
    #        via different feeds; (2) not the same at arrival as at
    #        dispatch (301 redirect); (3) not the same as the sitemap URLs.
    #        This will mean that RefetchControl will reget everything and
    #        massive numbers of duplicates will be got unless some kind of URL
    #        normalisation is done in self.parse_node:
    # http://feeds.reuters.com/~r/Reuters/UKTopNews/~3/GmNrSI5n5QE/uk-tesco-results-idUKKBN17D1GO
    # -> http://uk.reuters.com/articles/uk-tesco-results-idUKKBN17D1GO
    #        ... and probably also force-set meta['refetchcontrol_key'] to a
    #        hash of the normalised URL alone.
    sitemap_urls = ['http://uk.reuters.com/sitemap_index.xml']
    sitemap_follow = [gen_reuters_recent_regex(1)]

    def parse_page(self, response):
        """@url http://uk.reuters.com/article/us-heart-nih-funding-idUKKBN16Y2EI
        @returns items 1
        @scrapes bodytext bylines fetchtime firstpubtime modtime headline
        @scrapes keywords section source summary url
        """
        s = response.selector
        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.        
        mutate_selector_del(s, 'css', 'div.related-content')

        l = NewsLoader(selector=s)

        l.add_value('source', 'Reuters [UK]')

        # Add a number of items of data that should be standardised across
        # providers. Can override these (for TakeFirst() fields) by making
        # l.add_* calls above this line, or supplement gaps by making them
        # below.
        l.add_fromresponse(response)
        l.add_htmlmeta()
        l.add_schemaorg(response)
        #l.add_opengraph()
        l.add_scrapymeta(response)
        #l.add_schemaorg_bylines()
        #l.add_dublincore()

        l.add_xpath('bodytext',
                    '//span[@id="article-text"]/'
                        '*[not(@class="author")]//text()')
        l.add_xpath('summary',
                    '//meta[@name="description"]/@content')

        l.add_value('notes', 'fetchtime delayed by slow feed')

        return l.load_item()
