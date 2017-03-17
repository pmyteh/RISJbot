# -*- coding: utf-8 -*-
import scrapy.contracts
from scrapy.item import BaseItem
from scrapy.http import Request
from scrapy.exceptions import ContractFail

class NoScrapesContract(scrapy.contracts.Contract):
    pass
    """ Contract to check absence of fields in scraped items
        @noscrapes page_name page_body
    """

    name = 'noscrapes'

    def post_process(self, output):
        for x in output:
            if isinstance(x, (BaseItem, dict)):
                for arg in self.args:
                    if arg in x:
                        raise ContractFail("'%s' field is present" % arg)
