from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
import time

client = MongoClient('localhost', 27017)        #Подключается БД
db = client['mail_db']
all_mails = db.mails

class Parse_mail():         #класс для сбора почта
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument('start-maximized')
        self.driver = webdriver.Chrome(options=self.chrome_options)


    def get_in_mail(self):      #входим в почтовый ящик

        self.driver.get('https://account.mail.ru/login?page=https%3A%2F%2Fe.mail.ru%2Fmessages%2Finbox%2F&allow_external=1')
        elem = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.NAME, 'username')))
        elem.send_keys('study.ai_172')
        elem.send_keys(Keys.RETURN)
        time.sleep(1)                   #пришлось поставить отсрочку в секунду. через WebDriverWait не получилось
        elem = self.driver.find_element_by_name('password')
        elem.send_keys('NewPassword172')
        elem.send_keys(Keys.RETURN)

    def click_mails(self):          #ходим по письмам и собираем данные
        mail_list = self.collect_links()
        mail_info = []
        for click in mail_list:
            mail_dict = {}
            self.driver.get(click)
            elem = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, "//div[@class = 'letter__author']/span[@class = 'letter-contact']")))
            mail_dict['author'] = elem.find_element_by_xpath(
                "//div[@class = 'letter__author']/span[@class = 'letter-contact']").text
            mail_dict['author_mail'] = elem.find_element_by_xpath(
                "//div[@class = 'letter__author']/span[@class = 'letter-contact']").get_attribute('title')
            mail_dict['subject'] = elem.find_element_by_xpath(
                "//h2[@class='thread__subject thread__subject_pony-mode']").text
            mail_dict['date'] = elem.find_element_by_xpath('//div[@class="letter__date"]').text
            mail_text = elem.find_elements_by_xpath(
                '//div[@class="letter__body"]//tbody//span | //div[@class="letter__body"]//tbody//td | //div[@class="letter__body"]//p')
            mail_text_collect = [text.text for text in mail_text]
            mail_text_collect = [value for value in mail_text_collect if value]
            mail_text_collect = [self.clean_text(text) for text in mail_text_collect]


            mail_dict['text'] = mail_text_collect
            mail_info.append(mail_dict)


        return mail_info

    def clean_text(self, text):         #Пытаемся чистить текст, но большинство писем состоят из таблиц. потому чистим насколько возможно
        try:
            text = text.replace('\n', '')
            text = text.replace('\u200c', '')
            text = ' '.join(text.split())
        except:
            pass
        return text

    def collect_links(self):        #Собираем ссылки на письма

        time.sleep(5)
        inbox = self.driver.find_elements_by_xpath('//a[@href="/inbox/"]')
        for text in inbox:              #Получаем общее количество писем в ящике
            inbox = text.get_attribute("title")
        num_mail = [int(num) for num in filter(lambda num: num.isnumeric(), inbox.split())][0]
        mail_list = []
        while True:
            mails = self.driver.find_elements_by_class_name('js-letter-list-item')  #Ищем ссылки на странице

            for mail in mails:                  #Цикл для добавления ссылок в список
                link = mail.get_attribute('href')
                if link not in mail_list:           #Так как после скролла страниц ссылки не открываются все и могут повторяться, то вводим проверку на повторы
                    mail_list.append(link)
            if len(mail_list) == num_mail:         #Выходим из цикла While, если общее количество ссылок совпадает с количеством писем
                break
            self.scroll_page(mails)
        return mail_list

    def scroll_page(self, mails):       #Скролл страниц
        actions = ActionChains(self.driver)
        actions.move_to_element(mails[-1])
        actions.perform()

    def filldb(self):               #Заполняем базу данных
        self.get_in_mail()
        mail_info = self.click_mails()
        all_mails.insert_many(mail_info)
        self.driver.quit()

parse = Parse_mail()
parse.filldb()

