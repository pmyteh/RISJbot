# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

#import dateutil.parser
import dateparser
import logging
import re
from pprint import pprint
from gzip import compress
from base64 import b64encode
from w3lib.html import replace_escape_chars, replace_entities
from w3lib.html import remove_tags, remove_comments
from RISJbot.items import NewsItem
from RISJbot.metadata import RISJMetadataExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Identity, TakeFirst
from scrapy.loader.processors import Join, Compose, MapCompose

dateparsersettings = {'RETURN_AS_TIMEZONE_AWARE': True,}

logger = logging.getLogger(__name__)

def _remove_fluff(strl):
    for s in strl:
        if s.startswith('http'):
            continue
        yield re.sub(r'.*[Bb]y (.*)', r'\1', s).strip()

def _strip_strl(strl):
    for s in strl:
        yield s.strip()

def _split_and(strl):
    for s in strl:
        for tok in s.split(' and '):
            yield tok

def to_str(s):
    if isinstance(s, bytes):
        s = s.decode('utf-8')
    return s

def wrapped_parse(s):
    s = to_str(s)

    # Dateparser doesn't like millisecond precision in its strings.
    # 2017-02-27T18:02:16.787Z -> 2017-02-27T18:02:16Z
    s = re.sub(r'^([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})\.[0-9]+', r'\1', s)

    try:
        ns = dateparser.parse(s, settings=dateparsersettings)
    except TypeError:
        ns = None
    if not ns:
        logger.debug('Failed to parse date from: '+s)
    return ns


class NewsLoader(ItemLoader):
    default_item_class = NewsItem
    default_output_processor = TakeFirst()
        
    # fetchtime/modtime/firstpubtime: parse input to datetime.datetime,
    # write output as standard ISO format string
    fetchtime_in = MapCompose(wrapped_parse)#dateutil.parser.parse)
    fetchtime_out = Compose(TakeFirst(), lambda x: x.isoformat())
    modtime_in = MapCompose(wrapped_parse)#dateutil.parser.parse)
    modtime_out = Compose(TakeFirst(), lambda x: x.isoformat())
    firstpubtime_in = MapCompose(wrapped_parse)#dateutil.parser.parse)
    firstpubtime_out = Compose(TakeFirst(), lambda x: x.isoformat())

    clean_fn = MapCompose(lambda x: x.strip(),
                          lambda x: replace_escape_chars(x, replace_by=' '),
                          replace_entities,
                         )
    headline_in = clean_fn
    summary_in = clean_fn

    # Finding the body can be tricky. The Join() here allows multiple
    # attempts to be taken, as each (joined to a single string) body-try
    # will be a separate list entry, and the default TakeFirst() output
    # processor will choose the first non-empty one. So our highest-quality
    # extractor can be tried first, followed by a less-likely/lower quality
    # one, with a really broad option as a final fallback if desired.
    bodytext_in = Compose(#remove_comments,
                             #remove_tags,
                             Join(' '),
                             lambda x: replace_escape_chars(x, replace_by=' '),
                             replace_entities,
                            )
    bodytext_out = TakeFirst()
    
    rawpagegzipb64_out = Compose(TakeFirst(),
                                 compress,
                                 b64encode,
                                 lambda x: str(x, encoding='UTF-8'),
                                )

    # Store keywords and bylines as a comma-separated string (the native format
    # of most of the input formats). Export as a list, TakeFirst()ing the first
    # (best) string available.
    # TODO FIXME: This causes problems for bylines with titles in, e.g. the
    #             Daily Mail's "John Smith, Chief Political Reporter". Can
    #             either change the storage format, escape/unescape the comma,
    #             or erase the title in the Mail's input routine. 
    keywords_in = Compose(_strip_strl, Join(','))
    bylines_in = Compose(_strip_strl,
                         _remove_fluff,
                         _split_and,
                         Join(','))
    keywords_out = Compose(TakeFirst(),
                           lambda x: x.split(','),
                          )
    bylines_out = Compose(TakeFirst(), lambda x: x.split(','))

    # TODO: Consider converting these to use a proper RDFa/microdata parser
    #       like rdflib. scrapinghub/extruct looks ideal.
    # TODO: Consider splitting these out into a separate "processors" class,
    #       and/or allowing pre-processing of the selector to remove elements
    #       which we don't want in the output (such as BBC News captions?)
    #       before doing the extraction.

    def add_fromresponse(self, response):
        """Extracts standard data from the response object itself"""
        # TODO: Should be we using the canonicalised value of this from og:url
        #       or whatever to avoid dupes? Not important when taking a feed,
        #       but may be necessary to avoid duplicative crawls.
        self.add_value('url', response.url)
        self.add_value('rawpagegzipb64', response.body)
        self.add_value('fetchtime',
                       str(response.headers['Date'], encoding='utf-8'))
        # TODO: Consider (and check vs actual responses:)
        # self.add_value('modtime', str(response.headers['Last-Modified'], encoding='utf-8'))

    def add_htmlmeta(self):
        """Extracts the content potentially encoded in standard HTML meta tags,
           such as <meta name=author ...> and <meta name=keywords ...>.
           Extensions, such as the schema.org and Open Graph codings, are in
           their own methods."""
        self.add_xpath('bylines', 'head/meta[@name="author" or @property="author"]/@content')
        # self.add_xpath('bylines', '//a[@rel=author]/text()') # TODO: Check if needed
        # This is Google News specific
        self.add_xpath('keywords', 'head/meta[@name="news_keywords"]/@content')
        self.add_xpath('keywords', 'head/meta[@name="keywords"]/@content')

    def add_schemaorg(self, response, jsonld=True, microdata=True, rdfa=True):
        """Indirect to the add_schemaorg methods"""
        self.add_schemaorg_mde(response, jsonld=True, microdata=False, rdfa=False)
        self.add_schemaorg_by_xpath()

    def add_schemaorg_mde(self, response, jsonld=True, microdata=True, rdfa=True):
        mde = RISJMetadataExtractor(response,
                                    jsonld=jsonld,
                                    microdata=microdata,
                                    rdfa=rdfa,)

        data = mde.extract_newsarticle_schemaorg(jsonld=True)
        self.add_value('firstpubtime', data.get('datePublished'))
        self.add_value('modtime',      data.get('dateModified'))
        self.add_value('keywords',     data.get('keywords'))
        self.add_value('headline',     data.get('headline'))
        self.add_value('bodytext',     data.get('articleBody'))
        self.add_value('section',      data.get('articleSection'))
        try:
            self.add_value('bylines',  data['author']['name'])
        except (ValueError, KeyError):
            self.add_value('bylines',  data.get('author'))
        try:
            self.add_value('source',   data['publisher']['name'])
        except (ValueError, KeyError):
            self.add_value('source',   data.get('publisher'))

        
    def add_schemaorg_by_xpath(self):
        """Extracts the content encoded by the standards at schema.org,
           which consist of standard structured data added for the benefit of
           the major search engines. There are several ways to encode this;
           microdata uses @itemprop, RDFa Lite uses @property. There are
           subtle differences, but that's the big one. We'll try to handle
           both.

           The full schemas are *very* large, and variably implemented. We use
           only bits of it, mostly from NewsArticle and its parents.
        """
        #self.add_schemaorg_bylines()
   
        # These xpaths are fairly naive; in particular, they don't rely on
        # the presence of an appropriate 'itemscope' for microdata.

        # TODO: These dateXxxx are allowed to be dates, not times. Should
        #       probably check somewhere if they're not full times and push
        #       them to the bottom of the queue for those sites where
        #       that's true.
        self.add_xpath('firstpubtime', '//*[@itemprop="datePublished" or @property="datePublished"]/@content') # CreativeWork
        # self.add_xpath('firstpubtime', '//[@itemprop="dateCreated"]/@content]') # CreativeWork TODO: Check if needed - less apposite than datePublished
        self.add_xpath('modtime', '//*[@itemprop="dateModified" or @property="dateModified"]/@content') # CreativeWork
        self.add_xpath('keywords', '//*[@itemprop="keywords" or @property="keywords"]/@content') # CreativeWork 
        self.add_xpath('headline', '//*[@itemprop="headline" or @property="headline"]//text()') # CreativeWork 
        self.add_xpath('bodytext', '//*[@itemprop="articleBody" or @property="articleBody" or @itemprop="reviewBody" or @property="reviewBody"]//text()') # Article / Review
        self.add_xpath('section', '//*[@itemprop="articleSection" or @property="articleSection"]/@content') # Article

    def add_schemaorg_bylines(self):
        # This has a high false-positive rate, so is separated out.
        self.add_xpath('bylines', '//*[@itemprop="author"]//*[@itemprop="name"]//text()') # CreativeWork


    def add_opengraph(self):
        """Extracts the content encoded by the Open Graph Protocol, a means
           of marking up web objects used by Facebook to produce a rich social
           graph. The schema is at http://ogp.me. Dates are ISO 8601 strings.
        """
        # TODO: Can these be exposed as microdata instead of RDFa?
        self.add_xpath('source', 'head/meta[@property="og:site_name"]/@content')
        self.add_xpath('headline', 'head/meta[@property="og:title"]/@content')
        self.add_xpath('summary', 'head/meta[@property="og:description"]/@content')
        # There are also: og:type (normally 'article'), og:image
        # (representative image) og:url (canonical URL), og:audio (audio
        # representation), og:determiner (title preceeded by 'a'/'an'/...),
        # og:locale and og:locale:alternate (language_TERRITORY tags),
        # and og:video (complementary video URL)

        # These are OG tags for the 'article' subclass 
        self.add_xpath('modtime', 'head/meta[@property="article:modified_time"]/@content')
        self.add_xpath('firstpubtime', 'head/meta[@property="article:published_time"]/@content')
        self.add_xpath('section', 'head/meta[@property="article:section"]/@content')
        self.add_xpath('bylines', 'head/meta[@property="article:author"]/@content')
        # Also:
        # article:expiration_time - datetime - When the article is out of date after.
        # article:tag - string array - Tag words associated with this article.

    def add_dublincore(self):
        """Extracts Dublin Core metadata information from the head"""
        # TODO: arrange to extract properly? Will be better if the namespace
        #       is properly referenced in all the headers, but worse otherwise.
        #       May not be a good idea.
        self.add_xpath('headline', 'head/meta[@name="dc.title" or @name="DC.title"]/@content')
        self.add_xpath('summary', 'head/meta[@name="dcterms.abstract" or @name="DCTERMS.abstract"]/@content')
        self.add_xpath('summary', 'head/meta[@name="dc.description" or @name="DC.description"]/@content')
        self.add_xpath('modtime', 'head/meta[@name="dcterms.modified" or @name="DCTERMS.modified"]/@content')
        self.add_xpath('firstpubtime', 'head/meta[@name="dcterms.created" or @name="DCTERMS.created"]/@content')
        self.add_xpath('source', 'head/meta[@name="dc.publisher" or @name="DC.publisher"]/@content')
        #self.add_xpath('bylines', 'head/meta[@name="dc.creator" or @name="DC.creator"]/@content') # XXX? Valid for some docs, probably not for all.
        #self.add_xpath('language', 'head/meta[@name="dc.language" or @name="DC.language"]/@content')
        


    # TODO: def add_rNews():? Similar to the add_schemaorg work (which was
    #       based on it, but featuring different implementation.

    # TODO: def add_hNews():?

    def add_scrapymeta(self, response):
        """Extracts the content passed through meta tags from the Request. This
           is normally metadata from the RSS feed which linked to the article,
           and may in the future also be from Google News sitemaps."""
        try:
            from pprint import pformat
            logger.debug('Newsmeta: '+pformat(response.meta['newsmeta']))
            for k, v in response.meta['newsmeta'].items():
                self.add_value(k, v)
        except KeyError:
            pass

           
