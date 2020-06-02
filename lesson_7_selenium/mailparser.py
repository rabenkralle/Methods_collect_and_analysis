from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
chrome_options = Options()
import time
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome(options=chrome_options)
driver.get('https://account.mail.ru/login?page=https%3A%2F%2Fe.mail.ru%2Fmessages%2Finbox%2F&allow_external=1')
# time.sleep(1)
# elem = driver.find_element_by_name('username')
elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'username')))
elem.send_keys('study.ai_172')
elem.send_keys(Keys.RETURN)
time.sleep(1)
elem = driver.find_element_by_name('password')
elem.send_keys('NewPassword172')
elem.send_keys(Keys.RETURN)
time.sleep(5)
inbox = driver.find_elements_by_xpath('//a[@href="/inbox/"]')
for text in inbox:
    inbox = text.get_attribute("title")
num_mail = [int(num) for num in filter(lambda num: num.isnumeric(), inbox.split())][0]
mails = driver.find_elements_by_class_name('js-letter-list-item')
mail_list = []
for mail in mails:
    mail_list.append(mail.get_attribute('href'))
# print(mail_list)
mail_info = []
for click in mail_list:
    mail_dict = {}
    driver.get(click)
    elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class = 'letter__author']/span[@class = 'letter-contact']")))
    mail_dict['author'] = elem.find_element_by_xpath("//div[@class = 'letter__author']/span[@class = 'letter-contact']").text
    mail_dict['author_mail'] = elem.find_element_by_xpath("//div[@class = 'letter__author']/span[@class = 'letter-contact']").get_attribute('title')
    mail_dict['subject'] = elem.find_element_by_xpath("//h2[@class='thread__subject thread__subject_pony-mode']").text
    mail_dict['date'] = elem.find_element_by_xpath('//div[@class="letter__date"]').text
    mail_text= elem.find_elements_by_xpath('//div[@class="letter__body"]//tbody//span | //div[@class="letter__body"]//tbody//td | //div[@class="letter__body"]//p')
    mail_dict['text'] = [text.text for text in mail_text]
    mail_info.append(mail_dict)

print(mail_info)
# num_mails = 0
# while num_mails < num_mail:
#     # time.sleep(5)
#     mails = driver.find_elements_by_class_name('js-letter-list-item')
#     num_mails = len(mails)
#     print(num_mails)
#     actions = ActionChains(driver)
#     actions.move_to_element(mails[-1])
#     actions.perform()

# print(mails)

driver.quit