from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import pandas as pd
from pandas import json_normalize
import json

HEADER = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
          'Accept':'*/*'}

vacancy = input('Enter vacancy: ')
salary = input('Enter salary: ')

"""Создаем класс для поиска вакансий"""

class SearchVacancy:
    hh_link = 'https://hh.ru/'                      #Переменные с сылками на сайты
    sj_link = 'https://russia.superjob.ru/'

    @classmethod
    def get_text(cls, params):                #Получаем текст страницы с Headhunter

        html_hh = requests.get(f'{cls.hh_link}/search/vacancy', headers=HEADER,  params=params).text
        return html_hh

    @classmethod
    def get_text_sj(cls, params):              #Получаем текст страницы с SuperJob

        html_sj = requests.get(f'{cls.sj_link}/vacancy/search/', headers=HEADER, params=params).text
        return html_sj

    @classmethod
    def salary_split_hh(cls, salary_str):                   #Превращаем текстовое поле зарплат в int, параллельно очищая от лишних символов
        if '-' in salary_str:
            first_split = salary_str.split(' ')
            second_split = ''.join(i for i in first_split[0] if not i in '\xa0')
            third_split = second_split.split('-')
            vacancy_min_salary = int(third_split[0])
            vacancy_max_salary = int(third_split[1])
            vacancy_currency_salary = first_split[1]

        elif 'от' in salary_str:

            first_split = salary_str.split(' ')
            second_split = ''.join(i for i in first_split[1] if not i in '\xa0')
            vacancy_min_salary = int(second_split[0])
            vacancy_max_salary = None
            vacancy_currency_salary = first_split[2]

        elif 'до' in salary_str:

            first_split = salary_str.split(' ')
            second_split = ''.join(i for i in first_split[1] if not i in '\xa0')
            vacancy_min_salary = None
            vacancy_max_salary = int(second_split[0])
            vacancy_currency_salary = first_split[2]

        else:
            vacancy_min_salary = None
            vacancy_max_salary = None
            vacancy_currency_salary = None

        return vacancy_min_salary, vacancy_max_salary, vacancy_currency_salary

    @classmethod
    def salary_split_sj(cls, salary_str):  # Превращаем текстовое поле зарплат в int, параллельно очищая от лишних символов

        first_split = salary_str.split('\xa0')
        if '—' in salary_str:

            vacancy_min_salary = int(first_split[0] + first_split[1])
            vacancy_max_salary = int(first_split[3] + first_split[4])
            vacancy_currency_salary = first_split[5]

        elif 'до\xa0' in salary_str:

            vacancy_min_salary = None
            vacancy_max_salary = int(first_split[1] + first_split[2])
            vacancy_currency_salary = first_split[3]

        elif 'от\xa0' in salary_str:

            vacancy_min_salary = int(first_split[1] + first_split[2])
            vacancy_max_salary = None
            vacancy_currency_salary = first_split[3]

        else:
            vacancy_min_salary = None
            vacancy_max_salary = None
            vacancy_currency_salary = None

        return vacancy_min_salary, vacancy_max_salary, vacancy_currency_salary



    @classmethod
    def soup_info_hh(cls, salary, vacancy, page):                     #Парсим страницу HH и получаем список вакансий на странице

        params = {'salary': salary, 'text': vacancy, 'page': page}
        html_hh = cls.get_text(params)
        soup = bs(html_hh, 'lxml')
        next_page_button = soup.find('a', {'class': 'HH-Pager-Controls-Next'})
        vacancy_block = soup.find('div', {'class':'vacancy-serp'})
        vacancy_list = vacancy_block.findChildren(recursive=False)
        vacancies = []

        for vac in vacancy_list:
            vacancy_data = {}
            vacancy_name = vac.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})

            if vacancy_name:
                vacancy_data['name'] = vacancy_name.getText()
            else:
                continue

            vacancy_link = vac.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})['href']
            vacancy_salary = vac.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})

            if vacancy_salary:
                vacancy_data['min_salary'], vacancy_data['max_salary'], vacancy_data['currency'] = \
                    cls.salary_split_hh(vacancy_salary.getText())
            else:
                vacancy_data['min_salary'], vacancy_data['max_salary'], vacancy_data['currency'] = None, None, None

            vacancy_data['link'] = vacancy_link
            vacancy_data['site'] = 'HeadHunter'
            vacancies.append(vacancy_data)

        return vacancies, next_page_button

    @classmethod
    def soup_info_superjob(cls, salary, vacancy, page):         #Парсим страницу SuperJob и получаем список вакансий на странице

        params = {'keywords': vacancy, 'payment_value': salary, 'payment_defined': '1', 'page': page}
        html_sj = cls.get_text_sj(params)
        soup = bs(html_sj, 'lxml')
        next_page_button = soup.find('a', {'class': 'f-test-link-Dalshe'})          #SuperJob начал менять названия классов. Надо проверять
        vacancy_block = soup.find_all('div', {'class': '_2nteL'})
        vacancies = []

        for vac in vacancy_block:
            vacancy_data = {}
            vacancy_name = vac.find('a', {'class': '_1UJAN'})

            if vacancy_name:
                vacancy_data['name'] = vacancy_name.getText()
            else:
                continue

            vacancy_link = cls.sj_link + vac.find('a', {'class': '_1UJAN'})['href']
            vacancy_salary = vac.find('span', {'class': '_2VHxz'})

            if vacancy_salary:
                vacancy_data['min_salary'], vacancy_data['max_salary'], vacancy_data['currency'] = \
                    cls.salary_split_sj(vacancy_salary.getText())
            else:
                vacancy_data['min_salary'], vacancy_data['max_salary'], vacancy_data['currency'] = None, None, None

            vacancy_data['link'] = vacancy_link
            vacancy_data['site'] = 'Superjob'
            vacancies.append(vacancy_data)

        return vacancies, next_page_button

    @classmethod
    def click_pages(cls, vacancy, page = 0):                    #Перебор страниц в зависимости от наличия кнопки Дальше и сложение вакансий на страницах

        vacancies, next_page_button = cls.soup_info_hh(salary, vacancy, page)
        vacancies_hh = vacancies
        i = 0

        while next_page_button and i+1 != page:                 #У HH страницы нумеруются начиная с 0й.
            i += 1
            vacancies, next_page_button = cls.soup_info_hh(salary, vacancy, i)
            vacancies_hh.extend(vacancies)

        i = 1
        vacancies, next_page_button = cls.soup_info_superjob(salary, vacancy, i)
        vacancies_sj = vacancies

        while next_page_button and i != page:                   #У SJ страницы нумеруются начиная с 1й.
            i += 1
            vacancies, next_page_button = cls.soup_info_superjob(salary, vacancy, i)
            vacancies_sj.extend(vacancies)

        vacancies_full = vacancies_hh
        vacancies_full.extend(vacancies_sj)

        return vacancies_full
def main():

    hh = SearchVacancy()
    hh_full = hh.click_pages(vacancy)
    return hh_full


with open('vacancy_HH_SJ.json', 'w', encoding='utf8') as f:
    json.dump(main(), f, ensure_ascii=False)
df = pd.DataFrame(main())
pd.set_option('display.max_columns', None)
print(df)