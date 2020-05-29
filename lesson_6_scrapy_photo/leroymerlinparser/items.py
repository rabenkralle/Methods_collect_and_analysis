# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy.loader.processors import MapCompose, TakeFirst, Compose
import scrapy


def clean_list(value):
    value = value.replace('\n', '')
    try:
        value = float(''.join(filter(str.isdigit, value)))
    except:
        pass
    try:
        value = ' '.join(value.split())
    except:
        pass
    return value



class LeroymerlinparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst())
    photo = scrapy.Field()
    details = scrapy.Field(input_processor=MapCompose(clean_list))
    pass
