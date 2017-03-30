# -*- coding: utf-8 -*-

# Scrapy settings for RISJbot project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

from RISJbot.items import NewsItem
from scrapy.utils.project import data_path
import os

BOT_NAME = 'RISJbot'

SPIDER_MODULES = ['RISJbot.spiders',
                  'RISJbot.spiders.us',
                  'RISJbot.spiders.uk']
NEWSPIDER_MODULE = 'RISJbot.spiders'

# Location of templates for 'scrapy genspider' etc.
TEMPLATES_DIR = 'RISJbot/templates'

# Location of downloaded NLTK models etc. Need to set the environment variable
# so the NLTK libraries can find them.
NLTKDATA_DIR = data_path('nltk_data', createdir=True)
os.environ['NLTK_DATA'] = NLTKDATA_DIR

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'RISJbot (+http://reutersinstitute.politics.ox.ac.uk/)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# aws_credentials.py should set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
# in a similar manner to this file.
from .aws_credentials import *

# Configure the feed export. Relies on the AWS_* variables being correctly set.
FEED_URI = 's3://reutersinstitute-risjbot/test/JSONLinesItems/%(name)s/%(time)s-%(name)s.jsonl'
FEED_FORMAT = 'jsonlines'
# FEED_EXPORT_FIELDS = list(NewsItem().fields.keys()) # Critical for CSV
FEED_STORE_EMPTY = True
FEED_EXPORT_ENCODING = 'utf-8'
# FEED_EXPORT_ENCODING = None # UTF-8 except for JSON, which is ASCII-escaped

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# Note especially that high numbers are "close to the spider" (first to handle
# Requests, last to handle Responses) and low numbers are "close to the engine"
# (vice-versa)
SPIDER_MIDDLEWARES = {
    # NOTE: Subclassed as downloader middleware in a gross hack by
    #       OffsiteDownloaderShim. Don't load twice.
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': None,
    # Note: Should be before RefetchControl, to ensure that fetch gets logged:
    'RISJbot.spmiddlewares.risjfake404.RISJFake404': 222,
    # Note: Should be before any middleware which discards <scripts>:
    'RISJbot.spmiddlewares.risjextractjsonld.RISJExtractJSONLD': 300,
    'RISJbot.spmiddlewares.refetchcontrol.RefetchControl': 800,
    # Note: Should be after RefetchControl, to ensure that the URLs stored
    #       are the altered "canonical" ones.
    'RISJbot.spmiddlewares.equivalentdomains.EquivalentDomains': 900,
    'RISJbot.spmiddlewares.risjunwantedcontent.RISJUnwantedContent': 950,
}

# Enable RefetchControl, 8 fetches total, every 3 hours, including a
# trawl of previously-fetched pages for completeness (TN, 2017-03-15)
REFETCHCONTROL_ENABLED = True
REFETCHCONTROL_MAXFETCHES = 8
REFETCHCONTROL_REFETCHSECS = 10800
REFETCHCONTROL_REFETCHFROMDB = True
REFETCHCONTROL_RQCALLBACK = 'spider.parse_page'
REFETCHCONTROL_DIR = data_path('RefetchControl', createdir=True)

# Enable RISJUnwantedContent, stripping figures (TN, 2017-02-27)
RISJUNWANTEDCONTENT_ENABLED = True
RISJUNWANTEDCONTENT_XPATHS = ['//figure',
                              '//script',
                              '//style',
                              '//form',]

# Enable RISJFake404, dropping responses that are actually "page not found",
# but come with an improper HTTP 200 success code. Lookin' at you, foxnews.com.
RISJFAKE404_ENABLED = True
# List of ( url regex, matching xpath ) tuples
RISJFAKE404_DETECTIONSIGS = [
    ( r'https?://(www\.)?foxnews\.com/',
        '//h1[contains(., "Something has gone wrong")]'),
    ( r'https?://(www\.)?nbcnews\.com/',
        '//h2[contains(., "This live stream has ended")]'),
]

# Enable RISJExtractJSONLD; extract JSON-LD encoded metadata (TN, 2017-03-03)
RISJEXTRACTJSONLD_ENABLED = True

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'RISJbot.dlmiddlewares.offsitedownloadershim.OffsiteDownloaderShim': 100,
    'RISJbot.dlmiddlewares.risjstripnull.RISJStripNull': 543,
}

# AP returns responses will ASCII NUL bytes embedded in them.
# This is very bad for Scrapy's parsing code. Strip them.
RISJSTRIPNULL_ENABLED = True
RISJSTRIPNULL_SPIDERS = ['ap']

# Map all 'edition.cnn.com' URLs to the equivalent 'www.cnn.com' (dedupe)
# TN, 2017/03/27
EQUIVALENTDOMAINS_ENABLED = True
EQUIVALENTDOMAINS_MAPPINGS = {'www.cnn.com': 'edition.cnn.com'}

# Enable persistent storage in .scrapy (TN, 2017-02-09)
#DOTSCRAPY_ENABLED = True

# Disable the dupe filter: BaseDupeFilter is a no-op. If a filter is
# applied on top of RefetchControl, they both limit
# recrawls. This interaction may be undesirable (but is probably fine).
# (TN, 2017-02-14)
#DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'

# Close spider after 8.5 minutes, to allow for a 10 minute re-launch timer
# without overlap.
# TODO: Adjust to suit actual long-run crawl times
# TODO: May be better set in Scrapinghub, along with the re-launch timer
# Deleted: takes too long to stop to be really useful; just rely on
# scrapinghub refusing to queue the same crawl if it's already queued or
# running (TN: 2017-03-27)
#CLOSESPIDER_TIMEOUT = 510


# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy_dotpersistence.DotScrapyPersistence': 0,
    # Only designed to work on ScrapingHub - fiddle for local testing
#    'RISJbot.utils._risj_dotscrapy_indirect': 0,
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Persist the .scrapy directory via AWS
#DOTSCRAPY_ENABLED = True
#ADDONS_AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
#ADDONS_AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY
#ADDONS_AWS_USERNAME = "username"
#ADDONS_S3_BUCKET = 'reutersinstitute-risjbot'

# TODO: Add an ML metadata-generating pipeline
# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'RISJbot.pipelines.sentiment.Sentiment': 100,
    'RISJbot.pipelines.wordcount.WordCount': 200,
    'RISJbot.pipelines.namedpeople.NamedPeople': 300,
    'RISJbot.pipelines.striprawpage.StripRawPage': 900,
}

# Flag to determine storage of rawpagegzipb64 (to turn off for debugging)
# TN 2017/03/27
STRIPRAWPAGE_ENABLED = False


# A contract promising *not* to collect data for a particular field
# TN: 2017-02-27
SPIDER_CONTRACTS = {
    'RISJbot.contracts.NoScrapesContract': 10,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
