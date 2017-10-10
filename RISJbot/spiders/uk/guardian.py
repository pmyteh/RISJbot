# -*- coding: utf-8 -*-
from RISJbot.spiders.newssitemapspider import NewsSitemapSpider
from RISJbot.loaders import NewsLoader
from scrapy.loader.processors import Identity, TakeFirst
from scrapy.loader.processors import Join, Compose, MapCompose

class GuardianSpider(NewsSitemapSpider):
    name = "guardian"
    # allowed_domains = ["guardian.com"]
    sitemap_urls = ['https://www.theguardian.com/sitemaps/news.xml']

    def parse_page(self, response):
        """@url https://www.theguardian.com/business/2017/feb/20/how-unilever-foiled-kraft-heinzs-115m-takeover-bid-warren-buffett
        @returns items 1
        @scrapes bodytext fetchtime firstpubtime headline bylines
        @scrapes section source summary url modtime keywords
        """
        l = NewsLoader(response=response)

        l.add_value('source', 'The Guardian')

        # Add a number of items of data that should be standardised across
        # providers. Can override these (for TakeFirst() fields) by making
        # l.add_* calls above this line, or supplement gaps by making them
        # below.
        l.add_fromresponse(response)
        l.add_htmlmeta()
        l.add_schemaorg(response)
        l.add_opengraph()

        # Some Guardian articles are missing their OpenGraph article section
        # tag. These data-link-name tags are often multiple.
        l.add_xpath('section', '//a[@data-link-name="article section"]/text()', TakeFirst(), lambda x: x.strip())

        # The body tagging varies depending on the type of article, so let's
        # try several
        # TODO: There's still a bit of grot in this: <aside> tags, the social links
        #       under videos etc.
        # TODO: The <span class="drop-cap"> setup leaves a spurious line break
        #       after the first letter, which results in a space in the output
        #       text.
        l.add_xpath('bodytext', '//article//div[contains(@class, "content__main-column")]/*[not(contains(@class, "meta"))]//text()') # Eyewitness, plus video?

#        l.add_xpath('bodytext', '//div[@data-component="body"]//*[not(contains(@class, "meta"))]//text()') # Video
#        l.add_xpath('bodytext', '//div[@id="mainCol"]//text()') # Australian poll briefing
#        l.add_xpath('bodytext', '//ul[contains(@class, "gallery")]//text()') # In Pictures
#        l.add_xpath('bodytext', '//div[contains(@class, "gv-slice") and contains(@class, "second-strip")]//text()') # Interactive
#        #item['headline'] = join_strip_list(response.xpath('//h1//text()').extract()),
#        #item['bylines'] = response.xpath('//p[@class="byline"]//span[@itemprop="name"]/text()').extract(),

        return l.load_item()
