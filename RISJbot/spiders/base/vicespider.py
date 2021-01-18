# -*- coding: utf-8 -*-
from RISJbot.spiders.newssplashcrawlspider import NewsSplashCrawlSpider
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from itemloaders.processors import Identity, TakeFirst
from itemloaders.processors import Join, Compose, MapCompose

class ViceSpider(NewsSplashCrawlSpider):
    """This crawler is tricky on two separate grounds. First, Vice don't
       provide a pleasant Google News feed, or a sufficiently long RSS feed
       like our other publishers (the RSS feed is only five articles long, and
       for at least some editions stories are put out en bloc in the early
       morning). Consequently, this is a CrawlSpider collecting directly
       from the site. Secondly, Vice uses fairly heavy JavaScript preloading.
       The full text of most articles *is* available from a non-JS page, but
       unfortunately the /latest page is basically blank unless the JS is
       executed. So we fall back on Splash, a scriptable headless Python
       browser that works well with Scrapy (and can be obtained hosted on
       ScrapingHub for those going the cloud route).

       Note that there is also a GraphQL endpoint at
       https://www.vice.com/api/v1/graphql that may be suitable for an
       entirely different approach."""
    allowed_domains = ['vice.com']

    def parse_page(self, response):
        s = response.selector
        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.
        # CSS is better for operating on classes than XPath, otherwise
        # either will do.        
        #mutate_selector_del(s, 'xpath' '//*[@id='someid']')
        #mutate_selector_del(s, 'css', '.classname')

        l = NewsLoader(selector=s)

        # There are multiple articles in a single (JS-rendered) Vice page.
        # We are interested only in the first.
        # There are also, unhelpfully, several levels of <div>s with classes
        # containing "article__body". We only want the ultimate one.
        l.add_xpath('bodytext', '(//article)[1]//div[contains(@class, "article__body") and contains(@class, "bod-")]//text()')

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

        return l.load_item()
