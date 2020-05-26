# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from books.items import BooksItem

class Books24ruSpider(scrapy.Spider):
    name = 'books24ru'
    allowed_domains = ['book24.ru']

    def __init__(self, book_search):
        self.start_urls = [f'https://book24.ru/search/?q={book_search}']

    def parse(self, response):
        next_page = response.xpath("//a[@class='catalog-pagination__item _text js-pagination-catalog-item'][position() = last()]/@href").extract_first()
        book_links = response.xpath('//a[contains(@class, "book__title-link")]/@href')
        for link in book_links:
            yield response.follow(link, callback=self.book_parse)
        yield response.follow(next_page, callback=self.parse)

    def book_parse(self, response: HtmlResponse):
        name = response.xpath('//h1[@class="item-detail__title"]/text()').extract()
        author = response.xpath("//a[@class='item-tab__chars-link js-data-link']/text()").extract()
        old_price = response.xpath("//div[@class='item-actions__price-old']/text()").extract_first()
        new_price = response.xpath("//div[@class='item-actions__prices']//b/text()").extract_first()
        rating = response.xpath("//span[@class='rating__rate-value']/text()").extract_first()
        yield BooksItem(name=name, author=author, old_price=old_price, new_price=new_price, rating=rating)
