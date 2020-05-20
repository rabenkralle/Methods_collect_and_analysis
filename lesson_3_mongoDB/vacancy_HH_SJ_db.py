# 1) Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию, записывающую собранные вакансии в созданную БД
# 2) Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введенной суммы
# 3*)Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта

# import parsing_HH_SJ                      #Можно импортировать модуль, но для ускорения работы приложения сделано через json файл
from pprint import pprint
from pymongo import MongoClient
import pymongo
import json


client = MongoClient('localhost', 27017)        #Подключается БД
db = client['vacancy_db']
vacancies = db.vacancy

class Mongodb_fill():                           #Класс для заполнения БД, обновления и вывода информации согласно параметрам

    @classmethod
    def get_vacancy(cls):                        #Получаем вакансии из json файла
        with open('vacancy_HH_SJ.json', encoding='utf8') as f:
            vacancy_full = json.load(f)
        return vacancy_full

    @classmethod
    def fill_first_db(cls, vacancy):            #Проверка на существование коллекции и заполнение ее первичными данными
        if vacancies.estimated_document_count() == 0:
            return vacancies.insert_many(vacancy)

    @classmethod
    def vacancy_updater(cls):                   #Сравнение данных в базе с новыми данными и заполнение отсутствующих вакансий
        vacancy_full = cls.get_vacancy()
        cls.fill_first_db(vacancy_full)

        vacancydb_list = []
        for vacancy in vacancies.find({}, {'_id': 0}):
            vacancydb_list.append(vacancy)

        for item in vacancy_full:
            if item not in vacancydb_list:
                pprint(item)
                vacancies.insert_one(item)

    @classmethod
    def show_vacancy_params(cls):               #Выборка вакансий с ЗП больше 185000 в рублях
        for vacancy in vacancies.find({'$and':[{'$or': [{'min_salary': {'$gte': 185000}, 'max_salary': {'$gte': 185000}}]},{'currency':'руб.'}]}):
            pprint(vacancy)


def main():                                     #Запуск программы
    db_update = Mongodb_fill()
    print('--------------------')
    print('Добавленные вакансии:')
    db_update.vacancy_updater()
    print('--------------------')
    print('Вакансии с зарплатой выше 185000 рублей: ')
    db_update.show_vacancy_params()

main()
