# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ImmoCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    listingId = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    price = scrapy.Field()
    propertyType = scrapy.Field()
    rooms = scrapy.Field()
    superficy = scrapy.Field()
    description = scrapy.Field()
    time = scrapy.Field()
    city = scrapy.Field()
    zip_code = scrapy.Field()
    file_urls = scrapy.Field()
    status = scrapy.Field()
    pass
