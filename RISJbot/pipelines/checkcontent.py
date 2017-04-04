# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)

class CheckContent(object):
    def process_item(self, item, spider):
        if 'bodytext' not in item:
            u = item.get('url')
            if 'picture' not in u and 'video' not in u and 'gallery' not in u:
                logger.error("No bodytext: {}".format(u))
        return item
