# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from books.items import BooksItem

class LabirintruSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['labirint.ru']

    def __init__(self, book_search):
        self.start_urls = [f'https://www.labirint.ru/search/{book_search}']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//div[@class='pagination-next']/a[@class='pagination-next__text']/@href").extract_first()
        book_links = response.xpath('//a[@class = "product-title-link"]/@href')
        for link in book_links:
            yield response.follow(link, callback = self.book_parse)
        yield response.follow(next_page, callback = self.parse)



    def book_parse(self, response: HtmlResponse):
        name = response.xpath('//h1/text()').extract()
        link = response.url
        author = response.xpath('//div[@class = "authors"][1]/a/text()').extract()
        old_price = response.xpath('//span[@class="buying-priceold-val-number"]/text()').extract_first()
        new_price = response.xpath("//span[@class='buying-pricenew-val-number']/text()").extract_first()
        rating = response.xpath("//div[@id='rate']/text()").extract_first()
        yield BooksItem(name = name, link = link,  author = author, old_price = old_price, new_price = new_price, rating = rating)

