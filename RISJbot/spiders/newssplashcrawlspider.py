# -*- coding: utf-8 -*-
import logging
from scrapy.spiders import CrawlSpider
from scrapy.http import Request, HtmlResponse
from scrapy_splash import SplashRequest, SplashTextResponse
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

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
                meta={'originalurl': url},
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



