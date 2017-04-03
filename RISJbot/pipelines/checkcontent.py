# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)

class CheckContent(object):
    def process_item(self, item, spider):
        if 'bodytext' not in item:
            logger.error("No bodytext: {}".format(item.get('url'))
        return item
