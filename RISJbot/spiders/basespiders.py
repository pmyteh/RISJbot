# -*- coding: utf-8 -*-
import logging
from scrapy.spiders import XMLFeedSpider, SitemapSpider, CrawlSpider
from scrapy.http import Request, HtmlResponse
from scrapy_splash import SplashRequest, SplashTextResponse
from RISJbot.utils import NewsSitemap, etree_to_recursive_dict
from scrapy.utils.sitemap import sitemap_urls_from_robots#, Sitemap
from scrapy.spiders.sitemap import iterloc
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class NewsRSSFeedSpider(XMLFeedSpider):
    iterator = 'iternodes' # you can change this; see the docs
    itertag = 'item' # change it accordingly

    def parse_node(self, response, selector):
        nf = etree_to_recursive_dict(selector.root)[1]
        meta = {'RSSFeed': nf}
        # Extract URL and submit Request for crawling
        url = selector.xpath('link/text()').extract_first()
#        self.logger.debug('Meta: {}'.format(meta))
        if url:
            yield self.url_to_request(url, meta=meta)
        else:
            self.logger.debug('No URL for %s' % str(selector.extract()))

    def parse_page(self, response):
        raise NotImplementedError

    def url_to_request(self, url, callback=None, meta={}):
        if callback is None:
            callback = self.parse_page
        return Request(url.strip(), callback=callback, meta=meta)

class NewsAtomFeedSpider(XMLFeedSpider):
    iterator = 'iternodes' # you can change this; see the docs
    itertag = 'entry' # change it accordingly

    def parse_node(self, response, selector):
        for url in selector.xpath('link/@href').extract():
            yield self.url_to_request(url)

    def parse_page(self, response):
        raise NotImplementedError

    def url_to_request(self, url, callback=None, meta={}):
        if callback is None:
            callback = self.parse_page
        return Request(url.strip(), callback=callback, meta=meta)


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
                        yield self.url_to_request(loc,
                                                  callback=self._parse_sitemap)
            elif s.type == 'urlset':
                for loc, meta in self.iterurlset(s):
                    for r, c in self._cbs:
                        if r.search(loc):
                            try:
                                yield self.url_to_request(loc,
                                                          callback=c,
                                                          meta=meta)
                                break
                            except Exception as e:
                                self.logger.error("Failed to queue {}: {}".format(
                                                    loc, e))

    def url_to_request(self, url, callback=None, meta={}):
        if callback is None:
            callback = self.parse_page
        return Request(url.strip(), callback=callback, meta=meta)

    @staticmethod
    def iterurlset(it, alt=False):
        for d in it:
    #        logger.debug("{}".format(d))

            meta = {'NewsSitemap': d}
    #            meta = {'newsmeta': {}}
    #            nm = meta['newsmeta']

            loc = d['loc']

    #            if 'lastmod' in d:
    #                nm['modtime'] = d['lastmod'].strip()
    #            if 'news' in d:
    #                for k, v in d['news'].items():
    #                    if k == 'keywords':
    #                        nm['keywords'] = v.strip()
    #                    elif k == 'publication_date':
    #                        nm['firstpubtime'] = v.strip()
    #                    elif k == 'title':
    #                        nm['headline'] = v.strip()
            yield (loc, meta)

            # Also consider alternate URLs (xhtml:link rel="alternate")
            # NOTE: different interface than scrapy.spiders.SitemapSpider;
            #       depends (like the newsmeta code) on NewsSitemap.
            if alt:
                for k, v in d.items():
                    if k.startswith('alternate'):
                        yield (v, meta)

class NewsSplashCrawlSpider(CrawlSpider):
    """This is a subclass of CrawlSpider, which indirects its handling of
       both the start_urls and subsequently extracted and followed URLs via
       an instance of Splash, to render JS-heavy pages. Some of the method
       overrides are a little unpleasant, and this may break on Scrapy
       upgrades."""

    # Need to get access to settings to set this up properly for Splash, and
    # self.settings isn't instantiated until after __init__().
    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        splash_url = crawler.settings.get('SPLASH_URL', '')
        if not splash_url:
            raise Exception("SPLASH_URL must be configured")
        splash_host = urlparse(splash_url).hostname
        spider.allowed_domains.append(splash_host)
        if crawler.settings.get('SPLASH_HTTP_USER', None):
            spider.http_user = crawler.settings.get('SPLASH_HTTP_USER')
        if crawler.settings.get('SPLASH_HTTP_PASS', None):
            spider.http_pass = crawler.settings.get('SPLASH_HTTP_PASS')
        return spider

    # Send start_urls via Splash
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url,
                endpoint='render.html',
            )

    # Overridden to provide SplashRequest in place of Request for extracted
    # links
    def _build_request(self, rule, link):
        r = SplashRequest(url=link.url,
                          callback=self._response_downloaded)
        r.meta.update(rule=rule, link_text=link.text)
        return r

    # Overridden to handle SplashTextResponse; there is (currently) no Splash
    # response type which is correctly a subclass of HtmlResponse to make
    # CrawlSpider work properly with a Splash intermediary.
    # (see https://github.com/scrapy/scrapy/issues/2673)
    def _requests_to_follow(self, response):
        if not (isinstance(response, HtmlResponse) or
                isinstance(response, SplashTextResponse)):
            return
        seen = set()
        for n, rule in enumerate(self._rules):
            links = [lnk for lnk in rule.link_extractor.extract_links(response)
                     if lnk not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            for link in links:
                seen.add(link)
                r = self._build_request(n, link)
                yield rule.process_request(r)



