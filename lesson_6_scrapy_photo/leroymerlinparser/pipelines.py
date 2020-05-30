# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from scrapy.utils.python import to_bytes
import hashlib
import os

class LeroymerlinparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.leroymerlindb

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

class LeroymerlinItemEditor:
    def process_item(self, item, spider):
        try:
            item['details'] = [value for value in item['details'] if value]     #Убираем пустые значения в списке
        except:
            pass

        try:    #Переводим список в словарь
            item['details'] = {item['details'][i]: item['details'][i + 1] for i in range(0, len(item['details']), 2)}
        except Exception as e:
            print(e)

        try:
            item['price'] = float(item['price'])
        except:
            pass

        return item



class LeroymerlinPhotoPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        if item['photo']:
            for img in item['photo']:
                try:
                    yield scrapy.Request(img, meta={'item': item}) #Для создания папок по имени товара, собираем meta
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photo'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None): #Создаем папки
        item = request.meta['item']         #Используя meta, вытаскиваем данные item
        name = item['name']
        url = request.url
        media_guid = hashlib.sha1(to_bytes(url)).hexdigest()       #Формируем название файла фотографии
        media_ext = os.path.splitext(url)[1]
        return f'full/{name}/%s%s' % (media_guid, media_ext)
