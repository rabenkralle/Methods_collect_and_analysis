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
db = client['mvideo_top_db']
top_sales = db.mvideo

chrome_options = Options()
chrome_options.add_argument('start-maximized')
# chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)

driver.get('https://www.mvideo.ru/')
time.sleep(5)
assert "М.Видео" in driver.title
try:
    while True:
        button = driver.find_elements_by_xpath('//div[@class="gallery-layout"][2]//div[contains(@class, "sel-hits-block")]//a[@class = "next-btn sel-hits-button-next"]')
        button.click()
except:
    pass

elem = driver.find_elements_by_xpath('//div[@class="gallery-layout"]')
actions = ActionChains(driver)
actions.move_to_element(elem[2])
actions.perform()
button = driver.find_element_by_xpath('//div[@class="gallery-layout"][2]//div[contains(@class, "sel-hits-block")]//a[@class = "next-btn sel-hits-button-next"]')

while True:
    actions.move_to_element(button).click().perform()


elem = driver.find_elements_by_xpath('//div[@class="gallery-layout"][2]//div[contains(@class, "sel-hits-block")]//li[@class="gallery-list-item height-ready"]//a[@data-product-info]')
for el in elem:
    el = el.get_attribute('data-product-info')
    top_sale = insert_one(el)


