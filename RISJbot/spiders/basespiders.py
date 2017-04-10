# -*- coding: utf-8 -*-
import logging
from scrapy.spiders import XMLFeedSpider, SitemapSpider
from scrapy.http import Request
from RISJbot.utils import NewsSitemap
from scrapy.utils.sitemap import sitemap_urls_from_robots#, Sitemap
from scrapy.spiders.sitemap import iterloc

logger = logging.getLogger(__name__)

class NewsRSSFeedSpider(XMLFeedSpider):
    iterator = 'iternodes' # you can change this; see the docs
    itertag = 'item' # change it accordingly

    def parse_node(self, response, selector):
        meta = {'newsmeta': {}}
        nm = meta['newsmeta']

        # Extract (some) non-url parts of each sitemap node and pass in meta
        # tag
        title = selector.xpath('title/text()').extract_first()
        if title:
            nm['title'] = title.strip()

        description = selector.xpath('description/text()').extract_first()
        if description:
            nm['summary'] = description.strip()

        section = selector.xpath('category/text()').extract_first()
        if section:
            nm['section'] = section.strip()

        pubdate = selector.xpath('pubDate/text()').extract_first()
        if pubdate:
            nm['firstpubtime'] = pubdate.strip() # TODO: Maybe should be modtime?

        # Extract URL and submit Request for crawling
        url = selector.xpath('link/text()').extract_first()
        if url:
            yield Request(url.strip(), callback=self.parse_page, meta=meta)
        else:
            self.logger.debug('No URL for %s' % str(selector.extract()))

    def parse_page(self, response):
        raise NotImplementedError

class NewsAtomFeedSpider(XMLFeedSpider):
    iterator = 'iternodes' # you can change this; see the docs
    itertag = 'entry' # change it accordingly

    def parse_node(self, response, selector):
        for url in selector.xpath('link/@href').extract():
            yield Request(url.strip(), callback=self.parse_page)

    def parse_page(self, response):
        raise NotImplementedError
logger = logging.getLogger(__name__)


# TODO: Consider extending the NewsSitemapSpider to extract Google News metadata
#       from the XML sitemap, pass it using meta parameters through the spider
#       and extract here. May be more reliable, unlikely to be more complete
#       and probably won't work for all providers.
# In the mean time, indirect through NewsSitemapSpider to avoid having to
# change every spider if we get this going.
class NewsSitemapSpider(SitemapSpider):

    def start_requests(self):
        for url in self.sitemap_urls:
            # Add Meta key for collection in middleware, and passthrough key
            # for RefetchControl
            yield Request(url,
                          self._parse_sitemap,
                          meta={'sitemap': True,
                                'refetchcontrol_pass': True})

    def parse(self, response):
        return self.parse_page(response)

    def parse_page(self, response):
        raise NotImplementedError

    def _parse_sitemap(self, response):
        """This is adapted from scrapy.spiders.sitemap"""
        if response.url.endswith('/robots.txt'):
            for url in sitemap_urls_from_robots(response.text,
                                                base_url=response.url):
                yield Request(url, callback=self._parse_sitemap)
        else:
            body = self._get_sitemap_body(response)
            if body is None:
                self.logger.warning("Ignoring invalid sitemap: %(response)s",
                               {'response': response}, extra={'spider': self})
                return

            s = NewsSitemap(body)
            if s.type == 'sitemapindex':
                for loc in iterloc(s, self.sitemap_alternate_links):
                    if any(x.search(loc) for x in self._follow):
                        yield Request(loc, callback=self._parse_sitemap)
            elif s.type == 'urlset':
                for loc, meta in self.iterurlset(s):
                    for r, c in self._cbs:
                        if r.search(loc):
                            try:
                                yield Request(loc, callback=c, meta=meta)
                                break
                            except Exception as e:
                                self.logger.error("Failed to queue {}: {}".format(
                                                    loc, e))

    @staticmethod
    def iterurlset(it, alt=False):
        for d in it:
            logger.debug("{}".format(d))

            meta = {'newsmeta': {}}
            nm = meta['newsmeta']
            loc = d['loc']
            if 'lastmod' in d:
                nm['modtime'] = d['lastmod'].strip()
            if 'news' in d:
                for k, v in d['news'].items():
                    if k == 'keywords':
                        nm['keywords'] = v.strip()
                    elif k == 'publication_date':
                        nm['firstpubtime'] = v.strip()
                    elif k == 'title':
                        nm['headline'] = v.strip()
            yield (loc, meta)

            # Also consider alternate URLs (xhtml:link rel="alternate")
            # NOTE: different interface than scrapy.spiders.SitemapSpider;
            #       depends (like the newsmeta code) on NewsSitemap.
            if alt:
                for url in d:
                    if d.startswith('alternate'):
                        yield (url, meta)                                                    


# Following is from scrapy.spiders.sitemap. It's a bit grotty, and the Sitemap
# module doesn't seem optimised to do anything other than extract URLs.
"""


def iterloc(it, alt=False):
    for d in it:
        yield d['loc']

        # Also consider alternate URLs (xhtml:link rel="alternate")
        if alt and 'alternate' in d:
            for l in d['alternate']:
                yield l
"""
