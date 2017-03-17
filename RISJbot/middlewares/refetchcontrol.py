# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

#from scrapy_deltafetch.middleware import DeltaFetch

import logging
import os
import pickle
import datetime
import sqlite3

from twisted.enterprise import adbapi
from twisted.internet.defer import inlineCallbacks, returnValue
from scrapy.http import Request
from scrapy.item import BaseItem
from scrapy.utils.request import request_fingerprint
from scrapy.utils.project import data_path
from scrapy.utils.python import to_bytes
from scrapy.exceptions import NotConfigured, DontCloseSpider
from scrapy import signals


logger = logging.getLogger(__name__)

class RefetchControl(object):
    """
    This is a spider middleware to ignore requests to pages containing items
    seen in previous crawls of the same spider. It is a modified version of
    scrapy-deltafetch/DeltaFetch v1.2.1.

    RefetchControl differs from the parent DeltaFetch by offering more general
    control over repeated fetching:
     * The option of fetching (possibly limited numbers of) copies of an item, 
       at intervals of not less than a given time. This allows some sane change
       detection.
     * A mechanism for ensuring complete fetches, by trawling RefetchControl's
       database for insufficiently-fetched pages and scheduling them.

    It also depends on twisted.enterprise.adapi and sqlite3 rather than
    bsddb3.
    """

    def __init__(self, crawler):
        self.crawler = crawler
        s = crawler.settings
        self.dir = s.get('REFETCHCONTROL_DIR', os.getcwd())
        self.maxfetches = s.getint('REFETCHCONTROL_MAXFETCHES', 1)
        self.refetchsecs = s.getint('REFETCHCONTROL_REFETCHSECS', 0)
        self.refetchfromdb = s.getbool('REFETCHCONTROL_REFETCHFROMDB', False)
        self.reset = s.getbool('REFETCHCONTROL_RESET', False)
        # Grotty: see _schedule_url()
        self.rqcallback = s.get('REFETCHCONTROL_RQCALLBACK', 'spider.parse')
        self.dbpools = {}
        self.trawlstatus = "Not started"
        self.stats = crawler.stats
        logger.debug("RefetchControl starting. dir: {}, "
                     "maxfetches: {}, refetchsecs: {}, reset: {}, stats: {}"
                     "".format(self.dir,
                               self.maxfetches,
                               self.refetchsecs,
                               self.reset,
                               self.stats,
                              )
                    )

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('REFETCHCONTROL_ENABLED'):
            raise NotConfigured
        o = cls(crawler)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(o.spider_idle,   signal=signals.spider_idle)
        return o

    def spider_opened(self, spider):
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        dbpath = os.path.join(self.dir,
                              'RefetchControl-%s.sqlite' % spider.name)

        new = False
        if not os.path.isfile(dbpath):
            logger.debug("Can't find database file {}. Regenerating.".format(
                            dbpath))
            # Will need regenerating
            new = True

        detect_types = sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
        self.dbpools[spider.name] = adbapi.ConnectionPool(
                                        "sqlite3",
                                        dbpath,
                                        detect_types=detect_types,
                                        check_same_thread=False
                                    )


        if new or self.reset or getattr(spider, 'refetchcontrol_reset', False):
            # return Deferred to reset the database.
            return self.dbpools[spider.name].runInteraction(self._resetdb)

        
    def spider_closed(self, spider):
        for db in self.dbpools.values():
            db.close()

    def spider_idle(self, spider):
        logger.debug("spider_idle signal caught for {}.".format(spider.name))

        if self.refetchfromdb and self.trawlstatus == "Not started":
            logger.debug("Trawling database for unfetched pages.")
            self.trawlstatus = "In progress"
            d = self.dbpools[spider.name].runWithConnection(self._trawldb,
                                                            spider)
            d.addCallback(lambda _: setattr(self, 'trawlstatus', 'Done'))

        if self.trawlstatus == "In progress":
            # Trawl pending. Raising DontCloseSpider guarantees will be
            # called again.
            logger.debug("Raising DontCloseSpider")
            raise DontCloseSpider

    @staticmethod
    def _resetdb(c):
        logger.debug("Resetting RefetchControl database.")
        c.execute("DROP TABLE IF EXISTS records")
        c.execute("DROP INDEX IF EXISTS idx_fetches_time")
        c.execute("CREATE TABLE records (key bytes UNIQUE, url str, "
                    "fetches int, time timestamp, PRIMARY KEY(key)) "
                    "WITHOUT ROWID")
        c.execute("CREATE INDEX idx_fetches_time ON records (fetches, time)")

    def _trawldb(self, c, spider):
        """If an item is fetched once, but then disappears from the feed
           (pushed off the RSS list by new items, for example) it is not
           automatically refetched. For data completeness, this is an issue.
        
           Iterate the database's stored keys, check if any items are
           eligible. If so, queue Requests for them.

           If this is called only from spider_idle, there should be no race
           with the main process_spider_output throughput."""
        
        cutofft = (datetime.datetime.utcnow()
                        - datetime.timedelta(seconds=self.refetchsecs))
        for row in c.execute('SELECT * FROM records WHERE '
                                'time <= ? AND fetches < ?',
                             (cutofft, self.maxfetches)):
            _, url, nf, t = row
            tdiff = datetime.datetime.utcnow() - t
            logger.debug("Scheduling refetch from database crawl "
                         "({} fetches, last at {}, {:.0f} seconds ago, "
                         "min secs {}): {}".format(
                                 nf,
                                 t.isoformat(),
                                 tdiff.total_seconds(),
                                 self.refetchsecs,
                                 url,
                             )
                        )
            self._schedule_url(url, spider)
        logger.debug("_trawldb finished.")

    def _schedule_url(self, url, spider):
        # This is slightly problematic (but unavaoidable).
        # engine.crawl() is not a published interface, and is not
        # to be considered stable per the devs, though there is a
        # good deal of published code that uses it to schedule URLs
        # like this in the absence of an official alternative.
        #
        # FIXME: Furthermore, the callback is a problem: for spiders which
        #        inherit from XMLFeedSpider, the default spider.parse()
        #        parses the feed, not pages which are fetched from the
        #        feed. Consequently, the RISJ crawlers have implemented
        #        parse_page() as a standard interface for handling web page
        #        Responses, but this does not exist in all spiders. This
        #        makes this code fairly non-portable between spiders with
        #        different interfaces commingled in the same project :-(
        self.crawler.engine.crawl(Request(url, callback=eval(self.rqcallback)),
                                  spider)

    @inlineCallbacks
    def _process_request(self, r, spider):
        # Is Request; check if a fetch is allowed.
        key = self._get_key(r)

        l = yield self.dbpools[spider.name].runQuery(
                'SELECT url, fetches, time FROM records WHERE key=?', (key,))

        if len(l) == 0:
            # First fetch. Log and return.
            logger.debug("First fetch: {}".format(r))
            if self.stats:
                self.stats.inc_value('refetchcontrol/firstfetch',
                                     spider=spider)
            returnValue(r)

        # Fetched at least once.
        # Are we allowed another fetch? If so, have we waited the
        # minimum allowable period?
        url, nf, t = l[0]
        tdiff = datetime.datetime.utcnow() - t
        if (nf >= self.maxfetches or
               tdiff.total_seconds() < self.refetchsecs):
            # No. Drop.
            logger.debug("Ignoring already visited ({}/{} "
                         "fetches, last at {}, {:.0f} seconds "
                         "ago, min secs {}): {}".format(
                                 nf,
                                 self.maxfetches,
                                 t.isoformat(),
                                 tdiff.total_seconds(),
                                 self.refetchsecs,
                                 r,
                             )
                        )
            if self.stats:
                self.stats.inc_value('refetchcontrol/skipped',
                                     spider=spider)
            returnValue(None)
        # Yes. Log, add to stats, return
        logger.debug("Refetching ({} fetches, "
                     "last at {}, {:.0f} seconds ago, "
                     "min secs {}) {}".format(
                             nf,
                             t.isoformat(),
                             tdiff.total_seconds(),
                             self.refetchsecs,
                             r,
                         )
                    )
        if self.stats:
            self.stats.inc_value('refetchcontrol/refetched', spider=spider)
        returnValue(r)
        

    @inlineCallbacks
    def _process_item(self, item, response, spider):
        # Is Item; update the database with the new number of fetches
        # and timestamp, then pass the Item on.
        key = self._get_key(response.request)
        query = 'SELECT fetches FROM records WHERE key=?'
        l = yield self.dbpools[spider.name].runQuery(query, (key,))
        try:
            nf = l.pop()[0] + 1
        except IndexError:
            nf = 1

        url = response.url
        t = datetime.datetime.utcnow()
        query = ("INSERT OR REPLACE INTO records(key, url, fetches, time) "
                 "VALUES(?, ?, ?, ?)")
        yield self.dbpools[spider.name].runOperation(query, (key, url, nf, t))

        # TODO: Consider adding extra middleware to drop if it hasn't
        #       changed since the last fetch?
        if self.stats:
            self.stats.inc_value('refetchcontrol/stored', spider=spider)
        returnValue(item)
 
    @inlineCallbacks
    def process_spider_output(self, response, result, spider):
        for r in result:
            if isinstance(r, Request):
#                logger.debug("Is Request: {}".format(r))
                x = yield self._process_request(r, spider)
#                logger.debug("Have return value ({}) for {}".format(x, r))
                if x:
#                    yield r
                    returnValue([r])
                else:
                    # Drop
                    logger.debug("Dropping {}.".format(r))
                    continue

            elif isinstance(r, (BaseItem, dict)):
#                logger.debug("Is Item: {}".format(r))
                x = yield self._process_item(r, response, spider)
#                logger.debug("Have return value ({}) for {}".format(x, r['url']))
                returnValue([r])
#                yield r

    def _get_key(self, request):
        key = (request.meta.get('refetchcontrol_key') or
               request.meta.get('deltafetch_key') or
               request_fingerprint(request)
              )
        # request_fingerprint() returns string `hashlib.sha1().hexdigest()`
        return to_bytes(key)

