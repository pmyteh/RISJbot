# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)

class CheckContent(object):
    def process_item(self, item, spider):
        if 'bodytext' not in item:
            url = item.get('url')
            if 'picture' not in url and 'video' not in url:
                logger.error("No bodytext: {}".format(url))
        return item
