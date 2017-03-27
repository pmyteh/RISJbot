# -*- coding: utf-8 -*-
import re
import logging

logger = logging.getLogger(__name__)

def mutate_selector_del_xpath(selector, xpath_str):
    """Under the covers, Selectors contain an lxml.etree.Element document
       root, which is not exposed by the Selector interface. This is mutatable
       using the .remove method on parts of the selector.root document tree.
       Unfortunately, there is no native content removal interface in scrapy.

       As this is not using a published interface for Selector, it must be
       considered risky. In particular, it is feasible (though not likely) that
       scrapy could change its selector implementation to use a different
       HTML/XML parsing library, at which point this would fail.
    """
    for node in selector.root.xpath(xpath_str):
        node.getparent().remove(node)


    
def split_multiple_byline_string(s):
    for y in s.split(' and '):
        for tok in y.split(','):
            if re.search(r'(correspondent|reporter)', tok, flags=re.IGNORECASE):
                continue
            else:
                yield tok

import scrapy_dotpersistence
import os
from scrapy.exceptions import NotConfigured
# XXX This is all grot.
class _risj_dotscrapy_indirect(object):
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        os.environ["SCRAPY_PROJECT_ID"] = "persistence"
        os.environ["SCRAPY_SPIDER"] = "all-spiders"
        enabled = (settings.getbool('DOTSCRAPY_ENABLED') or
                   settings.get('DOTSCRAPYPERSISTENCE_ENABLED'))
        if not enabled:
            raise NotConfigured
        bucket = settings.get('ADDONS_S3_BUCKET')
        logger.debug('returning DotScrapyPersistence object')
        return scrapy_dotpersistence.DotScrapyPersistence(crawler, bucket)

#class SelectorXSLTTransformer(object):
#    def __init__(self, selector):
#        self.selector = selector
#        # self.root is an lxml.etree.Element, the output of:
#        # lxml.etree.fromstring(body, parser=parser, base_url=base_url)
#        # (from parsel, selector.py, function create_root_node)
#        # This keeps the scrapy code in use for actually creating selectors,
#        # for choosing a base lxml parser and coding based on the headers and
#        # for other bureaucracy.
#        self.doc = selector.root
#
#    def apply_stylesheet(self, xslt_str):
#        """Apply an XSLT stylesheet to the current document"""
#        transform = lxml.etree.XSLT(xslt_str)
#        self.doc = transform(self.doc)
#
#    def del_xpath(self, xpath_str):
#        """Delete all occurences of a given xpath from the current document"""
#        for bad in self.doc.xpath(xpath_str):
#            bad.getparent().remove(bad)
#
##    def clean_doc(self):
##        """Apply lxml.html.Cleaner to the current document iff HTML"""
##        if self.form == 'html':
##            self.doc = self.cleaner.clean_html(self.doc)
##        else:
##            raise NotImplementedError
#
#    def return_selector(self):
#        # Provide new Selector with amended content.
#        return Selector(root=self.doc)

