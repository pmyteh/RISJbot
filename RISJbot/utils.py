# -*- coding: utf-8 -*-
import re
import logging
import lxml.etree
from cssselect import HTMLTranslator

logger = logging.getLogger(__name__)

def mutate_selector_del(selector, method, expression):
    """Under the covers, Selectors contain an lxml.etree.Element document
       root, which is not exposed by the Selector interface. This is mutatable
       using the .remove method on parts of the selector.root document tree.
       Unfortunately, there is no native content removal interface in scrapy.

       As this is not using a published interface for Selector, it must be
       considered risky. In particular, it is feasible (though not likely) that
       scrapy could change its selector implementation to use a different
       HTML/XML parsing library, at which point this would fail.
    """
    try:
        if method == 'xpath':
            s = expression
        elif method == 'css':
            s = HTMLTranslator().css_to_xpath(expression)
        else:
            raise NotImplementedError

        for node in selector.root.xpath(s):
           node.getparent().remove(node)
    except Exception as e:
        logger.error('mutate_selector_del({}, {}, {},) failed: {}'.format(
                        selector,
                        method,
                        expression,
                        e))

def mutate_selector_del_xpath(selector, xpath_str):
    mutate_selector_del(selector, 'xpath', xpath_str)
 
def mutate_selector_del_css(selector, css_str):
    mutate_selector_del(selector, 'css', css_str)
    
def split_multiple_byline_string(s):
    for y in s.split(' and '):
        for tok in y.split(','):
            if re.search(r'(correspondent|reporter)', tok, flags=re.IGNORECASE):
                continue
            else:
                yield tok

class NewsSitemap(object):
    """Class to parse Sitemap (type=urlset) and Sitemap Index
    (type=sitemapindex) files. Adapted from scrapy.utils.sitemap."""

    def __init__(self, xmltext):
        xmlp = lxml.etree.XMLParser(recover=True,
                                    remove_comments=True,
                                    resolve_entities=False)
        self._root = lxml.etree.fromstring(xmltext, parser=xmlp)
        rt = self._root.tag
        self.type = self._root.tag.split('}', 1)[1] if '}' in rt else rt

    def __iter__(self):
        for elem in self._root.getchildren():
            d = etree_to_recursive_dict(elem)[1]

#            d = {}
#            for el in elem.getchildren():
#                tag = el.tag
#                name = tag.split('}', 1)[1] if '}' in tag else tag
#
#                if name == 'link':
#                    if 'href' in el.attrib:
#                        d.setdefault('alternate', []).append(el.get('href'))
#                else:
#                    d[name] = el.text.strip() if el.text else ''

            if 'loc' in d:
                yield d

def etree_to_recursive_dict(element):
    # Note: eliminates namespaces, like the original Sitemap
    tag = element.tag
    name = tag.split('}', 1)[1] if '}' in tag else tag

    txt = None
    if element.text:
        txt = element.text.strip()

    # Slightly less flexible than the standard implementation, in that
    # multiple alternates with the same language code (or None) will
    # clobber each other. Also needs support in the parsing code (different
    # interface).
    if name == 'link':
         if 'href' in element.attrib:
             return 'alternate{}'.format(element.get('hreflang')), \
                element.get('href')
    return name, dict(map(etree_to_recursive_dict, element)) or txt


#import scrapy_dotpersistence
#import os
#from scrapy.exceptions import NotConfigured
# XXX This is all grot.
#class _risj_dotscrapy_indirect(object):
#    @classmethod
#    def from_crawler(cls, crawler):
#        settings = crawler.settings
#        os.environ["SCRAPY_PROJECT_ID"] = "persistence"
#        os.environ["SCRAPY_SPIDER"] = "all-spiders"
#        enabled = (settings.getbool('DOTSCRAPY_ENABLED') or
#                   settings.get('DOTSCRAPYPERSISTENCE_ENABLED'))
#        if not enabled:
#            raise NotConfigured
#        bucket = settings.get('ADDONS_S3_BUCKET')
#        logger.debug('returning DotScrapyPersistence object')
#        return scrapy_dotpersistence.DotScrapyPersistence(crawler, bucket)

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

