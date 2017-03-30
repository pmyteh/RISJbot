# -*- coding: utf-8 -*-
import logging
import nltk
#import probablepeople
#import nameparser
from scrapy.exceptions import NotConfigured
#from import nltk_contrib import 

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

logger = logging.getLogger(__name__)

class NamedPeople(object):
    def __init__(self, crawler):
        self.crawler = crawler
        s = crawler.settings
        # Defaults to wherever NLTK normally keeps its data
        self.dir = s.get('NLTKDATA_DIR', None)
        # Ensure necessary NLTK data is present. This can be persisted across
        # runs using DotScrapy Persistence if on ScrapingHub.
        # TODO: Should check if they're present by trying to load them, then
        #       download on exception. nltk.download() checks if up to date
        #       as well, so this generates latency and network traffic.
        for pkg in ['maxent_ne_chunker',
                    'averaged_perceptron_tagger',
                    'punkt',
                    'words',
                   ]:
            nltk.download(pkg, download_dir=self.dir)

        logger.debug("NamedPeople starting; nltk_dir: {}".format(
                        self.dir)
                    )

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_item(self, item, spider):
        try:
            body = item['bodytext']
        except KeyError:
            return item

        # Chunk 'named entities' (people, places, organisations etc.) as 
        # (possibly hierarchical) nltk.Tree.
        namedEnt = nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(body)))
        # Find the ones tagged "PERSON" and extract them. Note that the NE
        # recognition code is far from perfect and will pick up some non-people
        # here. It's possible that we'd rather use a more robust library
        # (like the Stanford NER java library) but difficult to do in-process
        # on ScrapingHub.
        peopletup = [tuple(i.flatten()) for i in namedEnt if isinstance(i, nltk.Tree) and i.label() == "PERSON"]
        item['namedpeople'] = [' '.join(list(zip(*x))[0]) for x in peopletup]
        
        # Note that this will feature someone twice if they are mentioned
        # more than once. (e.g. "John Smith was found guilty ... Smith said: ")
        # TODO: de-dupe
#        firstnames = [nameparser.HumanName(x).first for x in people if len(nameparser.HumanName(x)) >= 2]
#        givennames = [y[0] for x in people for y in probablepeople.parse(x) if y[1] == 'GivenName']

        return item
