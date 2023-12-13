from pprint import pprint

import psycopg2
from config import connection
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import requests
from imp import DBManagerHelper



def employers_for_db():
    dict_ = {
            'ООО ИСЕРВ': 861271,
            'Tinkoff': 78638,
            'ASTON': 6093775,
            'ООО АпТрейдер (UpTrader)': 2365329,
            'Домклик': 2136954,
            'ООО Передовые технологии': 9150066,
            'AERODISK': 2723603,
            'LOGISTIX': 143735,
            'Soldoutmafia': 9511062,
            'Красное & Белое, розничная сеть': 1035394
    }
    return dict_



class DBManager:
    def __init__(self):
        self.cursor = connection.cursor()


    def get_companies_and_vacancies_count(self):
        pass

    def get_all_vacancies(self):
        pass

    def get_avg_salary(self):
        pass

    def get_vacancies_with_higher_salary(self):
        pass

    def get_vacancies_with_keyword(self):
        pass

    def get_vacancies_id(self, id):
        self.cursor.execute('SELECT customer_id FROM customers WHERE customer_id_hh = (%s)', [id])
        customer_id = self.cursor.fetchall()[0][0]
        return customer_id
        # self.cursor.execute('SELECT * FROM vacancies WHERE customer_id = %s', ([customer_id]))
        # return self.cursor.fetchall()

    def get_vacancies(self, id):
        customer_id = self.get_vacancies_id(id)
        self.cursor.execute('SELECT * FROM vacancies WHERE customer_id = %s', ([customer_id]))
        return self.cursor.fetchall()

    def post_employers_to_db(self, data):
        for key, value in data.items():
            self.post_employers_vacancies_to_db(value)
            self.cursor.execute("INSERT INTO customers(customer_name, customer_id_hh) VALUES (%s, %s)", (key, value))
        connection.commit()

    def post_employers_vacancies_to_db(self, id):
        req = requests.get(f'https://api.hh.ru/employers/{id}').json()
        open_vac = req['open_vacancies']
        if open_vac > 0:
            vacancies = req['vacancies_url']
            obj = DBManagerHelper()
            obj.create_dict_for_db(requests.get(vacancies, params={'only_with_salary': 'true'}).json(), id)
            return 'Ok', 202
        else:
            return 'Нет вакансий'

    def keyboard(self):
        keyboard_ = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

        self.cursor.execute("SELECT COUNT(customer_id) FROM customers")
        amount_iterations = self.cursor.fetchall()[0][0]

        self.cursor.execute("SELECT customer_name FROM customers")
        custs = self.cursor.fetchall()

        for i in range(amount_iterations):
            keyboard_.add(str(custs[i][0]))


        return keyboard_

    def get_info(self, emp_name):

        self.cursor.execute('SELECT * FROM customers WHERE customer_name = %s', (emp_name,))
        cust = self.cursor.fetchall()
        return cust

