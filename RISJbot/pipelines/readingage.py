# -*- coding: utf-8 -*-
import logging
import string
import unicodedata
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import download as nltk_download
from pronouncing import phones_for_word, syllable_count
from scrapy.exceptions import NotConfigured
#from import nltk_contrib import 

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

logger = logging.getLogger(__name__)

class ReadingAge(object):
    """Calculates the Flesch reading ease and Flesch-Kincaid grade level for
       article bodies. Valid only in English, partly as the tests don't
       transfer to other languages well, and partly because we rely on the
       CMU pronounciation dictionary for syllable counting, which is only
       available in en-US.

       NOTE: The definition of a 'sentence', a 'word', and a 'syllable', which
             necessary for these calculations, are not straightforward.
             Different tools provide different readability scores because they
             make choices as to what word tokenising algorithm and what
             syllable counting method they use. The choices here are
             sensible (nltk's pre-baked sentence and word tokenisers, plus
             a CMU pronounciation dictionary based syllable counter) but they
             are not the only possible ones. So results from different scoring
             programs are not strictly comparable. """

    def __init__(self, crawler):
        self.stats = crawler.stats
        s = crawler.settings
        # Defaults to wherever NLTK normally keeps its data
        self.dir = crawler.settings.get('NLTKDATA_DIR', None)
        self.dir = None
        # Ensure necessary NLTK data is present. This can be persisted across
        # runs using DotScrapy Persistence if on ScrapingHub.
        # TODO: Should check if they're present by trying to load them, then
        #       download on exception. nltk.download() checks if up to date
        #       as well, so this generates latency and network traffic.
        for pkg in ['punkt',
                    'words',
                   ]:
            nltk_download(pkg, download_dir=self.dir)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_item(self, item, spider):
        if 'bodytext' not in item:
            return item
        text = item['bodytext']
        sent = sent_tokenize(text)
        nsent = len(sent)
        words = list(self.strip_punct_toks(word_tokenize(text)))
        nwords = len(words)
        sylls = list(self.to_syl_count(self.split_hyphenated(words)))
        nsylls = sum(sylls)
        nsyllwords = len(sylls)
        if nsyllwords == 0 or nsent == 0:
            # No calculations for you.
            return item
        item['fleschreadingease'] = (206.835 -
                                     1.015 * (nwords / nsent) -
                                     84.6  * (nsylls / nsyllwords))
        item['kincaidgradelevel'] = (0.39  * (nwords / nsent) +
                                     11.8  * (nsylls / nsyllwords) -
                                     15.59)
        return item

    def to_syl_count(self, wordl):
        for word in wordl:
            try:
                # This uses the CMU dictionary of (American) pronounciations
                c = syllable_count(phones_for_word(word.lower())[0])
                self.stats.inc_value('readingage_in_cmu_dict')
                yield c
            except IndexError:
                # TODO: Should consider using a fallback rule/letter-based
                #       syllable counter in case the CMU pronouncing dictionary
                #       doesn't have the word. Not disastrous, as we use the
                #       full word count when calculating average sentence
                #       length, and only the words for which we have syllable
                #       counts when calculating average syllables.
                self.stats.inc_value('readingage_not_in_cmu_dict')

    @staticmethod
    def strip_punct_toks(l):
        punctuation_cats = set(['Pc', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Po'])
        punctuation_ascii = set(string.punctuation)
        for tok in l:
            ntok = ''.join(x for x in tok
                       if unicodedata.category(x) not in punctuation_cats
                          and x not in punctuation_ascii)
            if ntok:
                yield ntok

    @staticmethod
    def split_hyphenated(l):
        for tok in l:
            for stok in tok.split('-'):
                yield stok

