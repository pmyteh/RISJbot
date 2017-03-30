# -*- coding: utf-8 -*-
import logging
from scrapy.exceptions import NotConfigured
#from import nltk_contrib import 

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

logger = logging.getLogger(__name__)

class ReadingAge(object):
    def process_item(self, item, spider):
        raise NotImplementedError
        try:
            item['readingage'] = item['bodytext'].GETREADINGAGE())
        except KeyError:
            pass
        return item
