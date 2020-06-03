from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
import json
import time

client = MongoClient('localhost', 27017)        #Подключается БД
db = client['mvideo_top_db']
top_sales = db.mvideo

chrome_options = Options()                      #Выставляем опции драйвера и запускаем
chrome_options.add_argument('start-maximized')
# chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)

driver.get('https://www.mvideo.ru/')            #Входим на сайт Мвидео
time.sleep(5)
assert "М.Видео" in driver.title

elem = driver.find_elements_by_xpath('//div[@class="gallery-layout"]') #Ищем таблицы с товарами и спускаем по странице к нужному элементу
actions = ActionChains(driver)
actions.move_to_element(elem[2])
actions.perform()

while True:                         #Двигаемся к кнопке далее и нажимаем ее, если она есть
    try:
        button = driver.find_element_by_xpath(
            '//div[@class="gallery-layout"][2]//div[contains(@class, "sel-hits-block")]//a[@class = "next-btn sel-hits-button-next"]')
    except:
        break
    actions.move_to_element(button).click().perform()



items = driver.find_elements_by_xpath('//div[@class="gallery-layout"][2]//div[contains(@class, "sel-hits-block")]//li[@class="gallery-list-item height-ready"]//h4/a[@data-product-info]')

#Собираем все появившиеся товары

for item in items:      #Перебираем товары и закидываем в базу данных
    item = item.get_attribute('data-product-info')
    item = item.replace('\n', '')
    item = item.replace('\t','')
    item = json.loads(item)
    top_sales.insert_one(item)





driver.quit()
