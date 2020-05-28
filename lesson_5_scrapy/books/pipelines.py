# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import MongoClient

class BooksPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.booksdb

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item


class BooksItemEditor:
    def process_item(self, item, spider):
        if spider.name == 'labirintru':
            item['name'][0] = item['name'][0][item['name'][0].find(':') + 2:]
            if item['old_price']:
                item['old_price'] = int(item['old_price'])
            if item['rating']:
                item['rating'] = float(item['rating'])
        if spider.name == 'books24ru':
            if item['old_price']:
                item['old_price'] = item['old_price'].replace(' ','')
                item['old_price'] = item['old_price'].replace('р.', '')
                item['old_price'] = int(item['old_price'])
            item['new_price'] = item['new_price'].replace(' ','')
            if item['rating']:
                item['rating'] = item['rating'].replace(',', '.')
                item['rating'] = float(item['rating'])

        item['name'] = item['name'][0]
        item['new_price'] = int(item['new_price'])

        return item

