# -*- coding: utf-8 -*-

from extruct.rdfa import RDFaExtractor
from extruct.w3cmicrodata import MicrodataExtractor
from extruct.jsonld import JsonLdExtractor
from json.decoder import JSONDecodeError
from pprint import pformat
import logging
import re

logger = logging.getLogger(__name__)
class RISJMetadataExtractor(object):
    """An extruct-based metadata extractor"""
    # TODO: Extend to microdata and RDFa, replacing bespoke xpath code. Then
    #       test on body of crawlers!
    def __init__(self, response, microdata=False, jsonld=False, rdfa=False):
        self.response = response
        self.microdata = microdata
        self.jsonld = jsonld
        self.rdfa = rdfa

        if rdfa:
            try:
                self.rdfae = RDFaExtractor()
                self.rdfadata = self.rdfae.extract(self.response.text,
                                                   url=self.response.url)
            except JSONDecodeError:
                pass
        if microdata:
            try:
                self.mde = MicrodataExtractor()
                self.mdedata = self.mde.extract(self.response.text)
            except JSONDecodeError:
                pass
        if jsonld:
            try:
                self.jlde = JsonLdExtractor()
                self.jldata = self.jlde.extract(self.response.text)
            except (JSONDecodeError, TypeError):
                self.jldata = []
            finally:
                # Sometimes we get this in the meta dict from RISJExtractJSONLD
                self.jldata.extend(self.response.meta.get('json-ld', []))

    def extract_newsarticle_schemaorg(self,
                                      microdata=None,
                                      jsonld=None,
                                      rdfa=None):
        """Extract schema.org NewsArticle metadata, encoded using any
           supported metadata format. Note that we only try to extract the
           *first* block of NewsArticle data for each method (which is then
           combined with the first extracted from other methods if more than
           one is selected."""
        if microdata is None:
            microdata = self.microdata
        if jsonld is None:
            jsonld = self.jsonld
        if rdfa is None:
            rdfa = self.rdfa
        
        outd = {}
        if jsonld:
            for d in self.jldata:
#                logger.debug('Analysing JSON-LD data: '+pformat(d))
                try:
                    if (re.match(r'https?://schema.org/?', d['@context']) and
                            d['@type'] == 'NewsArticle'):
                        outd.update(d)
                except (KeyError, TypeError):
                    continue
        if microdata:
            for d in self.mdedata:
                logger.debug('Analysing W3C microdata: '+pformat(d))
                if re.match (r'https?://schema.org/NewsArticle/?', d.get('type', '')):
                    outd.update(d)
        if rdfa:
            raise NotImplementedError
#        logger.debug('Returning schema.org NewsArticle: '+pformat(outd))
        return outd
