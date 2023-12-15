from typing import List, Dict
from config import connection
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import requests
from imp import DBManagerHelper


class DBManager:
    def __init__(self):
        self.cursor = connection.cursor()

    def create_vacancie_table(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS vacancies(vacancie_id SERIAL PRIMARY KEY, customer_id INTEGER REFERENCES customers(customer_id), url varchar(255), payment INTEGER, requirements text, vacancie_name varchar(255))')

    def create_customers_table(self):
        self.cursor.execute('CREATE TABLE customers(customer_id serial PRIMARY KEY, customer_name varchar(255), customer_id_hh integer)')
    def get_companies_and_vacancies_count(self) -> List:
        self.cursor.execute('SELECT customers.customer_name, COUNT(vacancies.vacancie_id) as amount FROM customers LEFT JOIN vacancies ON customers.customer_id = vacancies.customer_id GROUP BY customers.customer_name;')
        return self.cursor.fetchall()

    def get_all_vacancies(self):
        self.cursor.execute('SELECT customers.customer_name, vacancies.vacancie_name, vacancies.payment, vacancies.url FROM vacancies JOIN customers ON customers.customer_id = vacancies.customer_id')
        return self.cursor.fetchall()

    def get_avg_salary(self):
        self.cursor.execute('SELECT AVG(payment) AS middle FROM vacancies')
        return int(self.cursor.fetchone()[0])

    def get_vacancies_with_higher_salary(self):
        avg_payment = self.get_avg_salary()
        self.cursor.execute('SELECT * FROM vacancies WHERE %s < payment', ([avg_payment]))
        return self.cursor.fetchall()

    def get_vacancies_with_keyword(self, keyword):
        self.cursor.execute('SELECT * FROM vacancies WHERE vacancie_name LIKE %s', ('%' + keyword + '%',))
        return self.cursor.fetchall()


    def get_employer_id(self, id: int) -> int:
        ''' Возвращает id работодателя '''

        self.cursor.execute('SELECT customer_id FROM customers WHERE customer_id_hh = (%s)', [id])
        customer_id = self.cursor.fetchall()[0][0]
        return customer_id

    def get_vacancies(self, id: int) -> List:
        ''' Возвращает вакансии по id работодателя, тоесть все вакансии нужного работодателя'''
        customer_id = self.get_employer_id(id)
        self.cursor.execute('SELECT * FROM vacancies WHERE customer_id = %s', ([customer_id]))
        return self.cursor.fetchall()

    def post_employers_to_db(self, data: Dict[str, int]) -> None:
        ''' Добавляет новых работодателей, на основании словаря переданного в функцию - {name: id(id работодателя на hh.ru)'''

        for key, value in data.items():
            self.post_employers_vacancies_to_db(value)
            self.cursor.execute("INSERT INTO customers(customer_name, customer_id_hh) VALUES (%s, %s)", (key, value))
        connection.commit()

    def post_employers_vacancies_to_db(self, id: int) -> str:
        '''Функция получающая информацию о работодателе'''

        req = requests.get(f'https://api.hh.ru/employers/{id}').json()
        open_vac = req['open_vacancies']
        if open_vac > 0:
            '''Получает url вакансий для парсинга, передает полученные вакансии по url(data) в функцию create_dict_for_db'''
            url_vacancie = req['vacancies_url']
            data = requests.get(url_vacancie, params={'only_with_salary': 'true'}).json()
            obj = DBManagerHelper()
            obj.create_dict_for_db(data, id) # Отправляет полученные вакансии для заполнения бд
            return 'Ok'
        else:
            return 'Нет вакансий'

    def keyboard(self):
        '''Возвращает клавиатуру для выбора работодателя'''
        keyboard_ = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

        self.cursor.execute("SELECT COUNT(customer_id) FROM customers")
        amount_iterations = self.cursor.fetchall()[0][0] # Количество итераций для добавления всех работодателей

        self.cursor.execute("SELECT customer_name FROM customers")
        custs = self.cursor.fetchall() # Имена работодателей в формате Список[кортеж(имя), кортеж(имя)]

        for i in range(amount_iterations):
            keyboard_.add(str(custs[i][0]))

        return keyboard_

    def get_info(self, emp_name) -> List:
        '''Возвращает всю информацию о работодателе по переданному в функцию имени'''
        self.cursor.execute('SELECT * FROM customers WHERE customer_name = %s', (emp_name,))
        cust = self.cursor.fetchall()
        return cust

