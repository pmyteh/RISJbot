# -*- coding: utf-8 -*-
import re

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

class SpecificFixupsPipeline(object):
    def process_item(self, item, spider):
        if spider.name == 'bbc':
            if 'bodytext' in item:
                # An embedded advertising code block in the body of BBC articles
                # is being left in by Scrapy's xpath text() selector.
                # TODO: This is <div class=bbccom_advert>, so could possibly
                #       be excluded by xpath on body fetch.
                item['bodytext'] = re.sub(r'/\*\*/.*?\(function\(\).*?/\*\*/', '', item['bodytext'])
                # TODO: Should probably exclude image and video captions more generally
                item['bodytext'] = re.sub(r'Image copyright.*?Image caption', '', item['bodytext'])
#            if 'bylines' in item:
#                item['bylines'] = [x for x in item['bylines'] if x != "https://www.facebook.com/bbcnews"]
        return item

