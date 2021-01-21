# -*- coding: utf-8 -*-
from RISJbot.spiders.newssitemapspider import NewsSitemapSpider
from RISJbot.spiders.newsrssfeedspider import NewsRSSFeedSpider
from RISJbot.spiders.newsspecifiedspider import NewsSpecifiedSpider
from RISJbot.spiders.newscsvfeedspider import NewsCSVFeedSpider
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
from RISJbot.loaders import NewsLoader
# Note: mutate_selector_del_xpath is somewhat naughty. Read its docstring.
from RISJbot.utils import mutate_selector_del
from itemloaders.processors import Identity, TakeFirst
from itemloaders.processors import Join, Compose, MapCompose
from scrapy.exceptions import CloseSpider
import logging
import json

logger = logging.getLogger(__name__)

class LiverpoolEchoSpiderParser(object):
    # No referrer headers should be set anywhere: the API calls are not
    # referrers of each other in any public sense.
    custom_settings = {
        'REFERRER_POLICY': 'no-referrer',
    }

    def start_requests(self):
        # This override of the start_requests function allows us to do setup
        # for comment fetching. In particular, it issues a request for bootstrap
        # data for the comment framework viafoura. This prevents the
        # usual requests from going out until this is in place.
        # We pick up the start_requests from the parent class in the callback
        # function.
        logger.debug('Fetching bootstrap data for Liverpool Echo comments')
        yield Request("https://api.viafoura.co/v2/www.liverpoolecho.co.uk/bootstrap/v2",
                      method="POST",
                      callback=self.parse_comments_bootstrap,
                      priority=100,
                      meta={# We don't even want to fetch robots.txt here.
                            'dont_obey_robotstxt': True})

    def parse_comments_bootstrap(self, response):
        data = json.loads(response.body)
        if data['http_status'] != 200:
            logger.error(f"Unable to fetch comments bootstrap data: {data}. Stopping crawl.")
            self.comments_bootstrap = None
        else:
            self.comments_bootstrap = json.loads(response.body)['result']
            logger.debug('Have bootstrap data. Now fetching news articles.')

        # Fall through to the usual items
        for item in super().start_requests():
            yield item

    def parse_page(self, response):
        """@url https://www.liverpoolecho.co.uk/news/liverpool-news/police-issue-warning-over-gift-19660932
        @returns items 1
        @scrapes bodytext bylines fetchtime firstpubtime modtime headline
        @scrapes keywords section source summary url language
        """
        s = response.selector
        # Remove any content from the tree before passing it to the loader.
        # There aren't native scrapy loader/selector methods for this.
        # CSS is better for operating on classes than XPath, otherwise
        # either will do.
        mutate_selector_del(s, 'xpath', '//aside')
        #mutate_selector_del(s, 'css', '.classname')

        l = NewsLoader(selector=s)

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

        l.add_xpath('articleid', '//meta[@property="article:id"]/@content')

        # We're going to try to scrape the comments. This is a little involved.
        # In order to get comments, we need two things:
        #   1. The site_uuid (which *should* probably be permanently fixed, but
        #      which live pages nevertheless bootstrap every time
        #   2. The content_container_uuid
        # The content_container_uuid can't be had without knowing both the site
        # uuid and the container_id (which is embedded in the page metadata).
        #
        # We have obtained the site_uuid at crawler startup using this class's
        # start_requests() function. But the content_container_uuid is different
        # for every article. So we need to fetch it now, and continue the
        # processing of this article in the callback.
        #
        # We are, therefore, going to yield a new Request, containing our
        # half-finished loader as a metadata item. The callback function for the
        # new Request will try to fetch comments and add them in, finishing by
        # yielding a complete Item for the crawler to handle.
        if l.get_xpath('//vf-conversations') and self.comments_bootstrap:
            site_uuid = self.comments_bootstrap['settings']['site_uuid']
            containerid = l.get_xpath('//meta[@name="vf:container_id"]/@content')[0]

            yield Request(f"https://livecomments.viafoura.co/v4/livecomments/{site_uuid}/contentcontainer/id?container_id={containerid}",
                          method="GET",
                          priority=5,
                          callback=self.parse_comments_get_contentcontainer,
                          errback=self.errback_comments,
                          cb_kwargs={'l': l,
                                     'site_uuid': site_uuid},
                          meta={# We don't even want to fetch robots.txt here.
                                'dont_obey_robotstxt': True})
        else:
            logger.debug(f'No comments section: {response.url}')
            l.add_value('notes', 'No comments section')
            yield l.load_item()

    def parse_comments_get_contentcontainer(self, response, l, site_uuid):
        # We tried to fetch the article comment metadata.
        # Did we get a good response?
        d = json.loads(response.body)
        try:
            content_container_uuid = d['content_container_uuid']
        except KeyError:
            logger.error(f'Unable to get the comments uuid for {l.get_output_value("url")}: {d}')
            raise StopIteration

        # Now we have everything we need to fetch the actual comments, via
        # another callback.
        yield Request(f"https://livecomments.viafoura.co/v4/livecomments/{site_uuid}/{content_container_uuid}/comments?limit=100",
                      method="GET",
                      priority=10,
                      callback=self.parse_comments,
                      errback=self.errback_comments,
                      cb_kwargs={'l': l,
                                 'site_uuid': site_uuid,
                                 'content_container_uuid': content_container_uuid},
                      meta={# We don't even want to fetch robots.txt here.
                            'dont_obey_robotstxt': True})

    def parse_comments(self, response, l, site_uuid, content_container_uuid):
        # We have the comments. If there were over 100 in total, we may need to
        # call ourselves recursively, passing part-filled loaders every time.
        d = json.loads(response.body)
        try:
            comments = d['contents']
        except KeyError:
            logger.error(f'Unable to get the comments for {l.get_output_value("url")}: {d}')
            raise StopIteration

        last_comment_uuid = None
        for comment in comments:
            l.add_value('rawcomments', json.dumps(comment))
            try:
                last_comment_uuid = comment['content_uuid']
            except KeyError:
                logger.debug(f'No content_uuid found for comment {comment}')
            try:
                l.add_value('comments', comment['content'])
            except KeyError:
                # If comments have been deleted, for example, they don't have
                # a 'content' entry.
                l.add_value('comments', '')

        if 'more_available' in d and d['more_available']:
            logger.debug(f'More than one page of comments for {l.get_output_value("url")}: fetching next page')
            yield Request(f"https://livecomments.viafoura.co/v4/livecomments/{site_uuid}/{content_container_uuid}/comments?limit=100&starting_from={last_comment_uuid}",
                          method="GET",
                          priority=15,
                          callback=self.parse_comments,
                          errback=self.errback_comments,
                          cb_kwargs={'l': l,
                                     'site_uuid': site_uuid,
                                     'content_container_uuid': content_container_uuid},
                          meta={# We don't even want to fetch robots.txt here.
                                'dont_obey_robotstxt': True})

        else:
            if 'more_available' not in d:
                logger.warning(f"No 'more_available' key found at {request.url} for {l.get_output_value('url')}")
            yield l.load_item()

    def errback_comments(self, failure):
        logging.warning("Failed to collect all comments. Saving whatever we've got.")
        l = failure.request.cb_kwargs['l']
        logging.info(failure)
        l.add_value('notes', 'Failure in comment collection')
        yield l.load_item()


class NewsSitemapLiverpoolEchoSpider(LiverpoolEchoSpiderParser, NewsSitemapSpider):
    name = "liverpoolechositemap"
    # allowed_domains = ['www.liverpoolecho.co.uk']
    # A list of XML sitemap files, or suitable robots.txt files with pointers.
    sitemap_urls = ['https://www.liverpoolecho.co.uk/map_news.xml']

class NewsSpecifiedLiverpoolEchoSpider(LiverpoolEchoSpiderParser, NewsSpecifiedSpider):
   name = "liverpoolechospecified"


