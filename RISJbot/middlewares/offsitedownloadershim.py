# -*- coding: utf-8 -*-

import logging
from scrapy.exceptions import IgnoreRequest
from scrapy.spidermiddlewares.offsite import OffsiteMiddleware

logger = logging.getLogger(__name__)

class OffsiteDownloaderShim(OffsiteMiddleware):
    """This is a shim to adapt the existing OffsiteMiddleware spider
       middleware as downloader middleware. This lets it properly discard
       offsite redirects from non-spider sources (such as those generated
       from the independent.co.uk sitemap.

       See https://github.com/scrapy/scrapy/issues/2241

       FIXME: It goes without saying that this kind of hack is full of grot.
    """

    def process_request(self, request, spider):
        """Handle a Request, as downloader middleware, by smashing it through
           the base class's (spider middleware) process_spider_output() to see
           if we want to keep it. Then take appropriate action (the interface
           of these two kinds of middleware is quite different."""

        # process_spider_output takes a response, which it (currently) doesn't
        # use, an iterable of Requests and/or Items, and a spider. It yields
        # those objects which are not to be dropped.
        #
        # We pass the single request (in a list). If we get it back, we should
        # continue to fetch it, so return None. If we don't, it should be
        # dropped, so raise IgnoreRequest.
        l = list(self.process_spider_output(response=None,
                                            result=[request],
                                            spider=spider))

        if not l:
            raise IgnoreRequest
        return None


