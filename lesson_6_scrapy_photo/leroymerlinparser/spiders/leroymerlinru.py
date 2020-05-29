# -*- coding: utf-8 -*-
import scrapy
# from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from leroymerlinparser.items import LeroymerlinparserItem

class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']
    # start_urls = ['http://leroymerlin.ru/']
    def __init__(self, text):
        self.start_urls = [f'https://leroymerlin.ru/search/?q={text}']

    def parse(self, response):
        next_page = response.xpath('//a[@class = "paginator-button next-paginator-button"]/@href').extract_first()
        item_links = response.xpath('//div[@class = "product-name"]/a/@href').extract()
        for link in item_links:
            yield response.follow(link, callback=self.item_parse)
        yield response.follow(next_page, callback=self.parse)

    def item_parse(self, response):
        loader = ItemLoader(item=LeroymerlinparserItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_value('link', response.url)
        loader.add_xpath('price', '//span[@slot = "price"]/text()')
        loader.add_xpath('photo', '//picture[@slot = "pictures"]/img/@src')
        loader.add_xpath('details', '//div[@class = "def-list__group"]//text()')
        yield loader.load_item()

