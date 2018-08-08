# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import logging
from scrapy.exceptions import NotConfigured


logger = logging.getLogger(__name__)

class UnwantedContent(object):
    """Spider middleware to process a response's selector by removing a
       (configurable) set of elements from it. This is used to strip things
       like figures from the content before passing the body on to the parsing
       code. This makes it feasible to strip similar junk from all pages if
       necessary.

       Note that this leaves response.selector and response.body containing
       different data. This is (1) an advantage, as it lets the spider save
       the original page, and (2) a disadvantage, as the 'response' object
       is confusingly no longer coherent. Caller beware!

       Under the covers, Selectors contain an lxml.etree.Element document
       root, which is not exposed by the Selector interface. This is mutatable
       using the .remove method on parts of the selector.root document tree.
       Unfortunately, there is no native content removal interface in scrapy.

       As this is not using a published interface for Selector, it must be
       considered risky. In particular, it is feasible (though not likely) that
       scrapy could change its selector implementation to use a different
       HTML/XML parsing library, at which point this would fail.
    """
    def __init__(self, settings):
        if not settings.getbool('UNWANTEDCONTENT_ENABLED'):
            raise NotConfigured
        self.xpaths = settings.get('UNWANTEDCONTENT_XPATHS')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_spider_input(self, response, spider):
        # This can pick up initial (possibly gzipped) sitemap
        # Responses, before they have made it to the Spider and been decoded.
        # In any case, we don't want to edit sitemap files (or RSS for that
        # matter. Filter this strictly to non-sitemap objects.

        try:
            sel = response.selector
        except AttributeError:
#            logger.warning("No selector for {}; probably non-HTML".format(
#                                    response))
            return None

        if not response.meta.get('sitemap'):
            for xpath_str in self.xpaths:
                for node in sel.root.xpath(xpath_str):
                    node.getparent().remove(node)
        return None # Success


