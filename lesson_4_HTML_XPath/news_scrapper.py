# 1)Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex.news
# Для парсинга использовать xpath. Структура данных должна содержать:
# * название источника,
# * наименование новости,
# * ссылку на новость,
# * дата публикации
#
# 2)Сложить все новости в БД

from lxml import html
import requests
import datetime
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



HEADER = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
          'Accept':'*/*'}

mailru_link = 'https://news.mail.ru/'
yandexru_link = 'https://yandex.ru/news/'
lentaru_link = 'https://lenta.ru/'

class Scrapper():       #Создаем класс для сбора новостей с сайтов

    @classmethod
    def get_text(cls, main_link):           #Получаем информацию со страницы в виде текста
        response = requests.get(main_link, headers = HEADER)
        dom = html.fromstring(response.text)
        return dom

    @classmethod
    def parse_yandex_ru(cls):               #Собираем новости с сайта Яндекс
        yandex = 'https://yandex.ru'
        dom = cls.get_text(yandexru_link)
        text = dom.xpath("//div[@aria-label]//h2/a[@class]/text()")
        link = dom.xpath("//div[@aria-label]//h2/a[@class]/@href")
        info_news = dom.xpath("//div[@aria-label]//div[@class = 'story__date']/text()")
        news = []
        for i in range(len(text)):
            data = {}
            data['Title'] = text[i]
            data['Link'] = yandex + link[i]
            info_split = info_news[i].split(sep=' ')        #Так как время и источник на Яндексе собраны в одном поле, то разделяем полученные данные
            t = ''
            for j in info_split:
                if j != info_split[-1]:
                    t = t + j + ' '
            data['Source'] = t
            data['Time'] = str(datetime.date.today()) + ' ' + info_split[-1]  #К сожалению, в Яндексе указывается время без даты, потому используется библиотека datetime,
                                                                                # но нет проверки, если смотришь после 0 часов, а новости предыдущим днем
            news.append(data)

        return news

    @classmethod
    def parse_lenta_ru(cls):                #Собираем новости с сайта Лента.ру

        dom = cls.get_text(lentaru_link)
        news = []
        text = dom.xpath('//div/section[contains(@class,"b-top7-for-main")]//div[contains(@class, "item")]//a[not(contains(@class, "title-pic")) and not(contains(@class, "b-favorite__item"))]/text()')
        link = dom.xpath('//div/section[contains(@class,"b-top7-for-main")]//div[contains(@class, "item")]//a[not(contains(@class, "title-pic")) and not(contains(@class, "b-favorite__item"))]/@href')
        time = dom.xpath('//div/section[contains(@class,"b-top7-for-main")]//div[contains(@class, "item")]//a[not(contains(@class, "title-pic")) and not(contains(@class, "b-favorite__item"))]/time/@datetime')
        for i in range(len(text)):
            data = {}
            data['Title'] = text[i].replace('\xa0', ' ')
            data['Link'] = lentaru_link + link[i]
            data['Source'] = 'Lenta.ru'
            data['Time'] = time[i]
            news.append(data)

        return news

    @classmethod
    def parse_mail_ru(cls):         #Собираем информацию с сайта Мейл.ру

        dom = cls.get_text(mailru_link)
        text = dom.xpath('//div[contains(@class, "topnews")]//div[contains(@class, "daynews")]//span/span[1]/text()')
        link = dom.xpath('//div[contains(@class, "topnews")]//div[contains(@class, "daynews")]//a/@href')
        source_link = '//div[contains(@class, "breadcrumbs")]//a[contains(@class, "breadcrumbs")]/span/text()'
        time_link = '//div[contains(@class, "breadcrumbs")]//span[@datetime]/@datetime'
        news = []

        for i in range(len(text)):
            data = {}
            data['Title'] = text[i].replace('\xa0', ' ')
            data['Link'] = mailru_link + link[i]
            data['Source'] = cls.change_page(data['Link'], source_link)[0]
            data['Time'] = cls.change_page(data['Link'], time_link)[0]
            news.append(data)

        return news

    @classmethod
    def change_page(cls, link, source_time_link):       #Переход по страницым для сбора доп. информации
        dom = cls.get_text(link)
        news_link = dom.xpath(source_time_link)
        return news_link

    @classmethod
    def all_news(cls):                                  #Объединение собранных новостей
        yandex_news = cls.parse_yandex_ru()
        lenta_news = cls.parse_lenta_ru()
        mail_news = cls.parse_mail_ru()
        news = yandex_news
        news.extend(lenta_news)
        news.extend(mail_news)
        return news

'''Создаем базу для переноса новостей в SQLite'''

engine = create_engine('sqlite:///news.db',echo=True)
Base = declarative_base()

class News(Base):                       #класс для создания структуры БД
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    title = Column(String(255))
    link = Column(String(255))
    source = Column(String)
    time = Column(String)

    def __init__(self,title, link, source, time):
        self.title = title
        self.link = link
        self.source = source
        self.time = time

def main():

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    sc = Scrapper()
    session = Session()

    for article in sc.all_news():                               #Заполняем БД данными
        session.add(News(article['Title'], article['Link'], article['Source'], article['Time']))

    for instance in session.query(News).filter():                  #Смотрим, что есть в БД
        print(instance.title, instance.source, instance.time, instance.link)

    session.commit()
    session.close()

main()