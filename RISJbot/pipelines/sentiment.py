# -*- coding: utf-8 -*-
import logging
from scrapy.exceptions import NotConfigured
from textblob import TextBlob

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

logger = logging.getLogger(__name__)

class Sentiment(object):
    def process_item(self, item, spider):
        try:
            blob = TextBlob(item['bodytext'])
            item['sentiment'] = blob.sentiment.polarity
        except KeyError:
            pass
        return item
