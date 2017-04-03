# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)

class CheckContent(object):
    def process_item(self, item, spider):
        try:
            item['bodytext']
        except KeyError:
            logger.error("No bodytext: {}".format(item.url))
        return item
