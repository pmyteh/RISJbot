# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsItem(scrapy.Item):
    source = scrapy.Field()
    url = scrapy.Field()
    originalurl = scrapy.Field()
    fetchtime = scrapy.Field()
    modtime = scrapy.Field()
    firstpubtime = scrapy.Field()
    section = scrapy.Field()
    headline = scrapy.Field()
    summary = scrapy.Field()
    bylines = scrapy.Field()
    bodytext = scrapy.Field()
#    numimages = scrapy.Field()
#    numvideos = scrapy.Field()
    keywords = scrapy.Field()
    rawpagegzipb64 = scrapy.Field()
    previousfetches = scrapy.Field()
    notes = scrapy.Field()
    language = scrapy.Field()
    articleid = scrapy.Field()
    rawcomments = scrapy.Field()
    comments = scrapy.Field()
    # The following are added by pipeline
    wordcount = scrapy.Field()
    sentiment = scrapy.Field()
    subjectivity = scrapy.Field()
    namedpeople = scrapy.Field()
    female = scrapy.Field()
    kincaidgradelevel = scrapy.Field()
    fleschreadingease = scrapy.Field()
