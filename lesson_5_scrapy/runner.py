from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from books import settings
from books.spiders.labirintru import LabirintruSpider
from books.spiders.books24ru import Books24ruSpider


if __name__ == '__main__':
	crawler_settings = Settings()
	crawler_settings.setmodule(settings)
	process = CrawlerProcess(settings = crawler_settings)
	process.crawl(LabirintruSpider, book_search = 'программирование')
	process.crawl(Books24ruSpider, book_search = 'программирование')
	process.start()