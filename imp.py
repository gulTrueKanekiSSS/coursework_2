from config import connection


class DBManagerHelper:
    def __init__(self):
        self.cursor = connection.cursor()

    def create_dict_for_db(self, data, id):
        dict_ = {}

        self.cursor.execute('SELECT customer_id FROM customers WHERE customer_id_hh = (%s)', [id])
        customer_id = self.cursor.fetchall()[0][0]
        self.cursor.execute('SELECT customer_id FROM vacancies WHERE customer_id = %s', ([customer_id]))
        if len(self.cursor.fetchall()) > 0:
            print('Такое уже существует')
        else:
            for item in data['items']:
                dict_['vacancie_name'] = item['name']
                dict_['requirements'] = item['snippet']['requirement']
                dict_['url'] = item['alternate_url']
                if item['salary']['to'] is not None:
                    dict_['payment'] = item['salary']['to']
                else:
                    dict_['payment'] = item['salary']['from']
                self.cursor.execute('INSERT INTO vacancies(customer_id, url, payment, requirements, vacancie_name) VALUES (%s, %s, %s, %s, %s)', (customer_id, dict_['url'], dict_['payment'], dict_['requirements'], dict_['vacancie_name']))
                connection.commit()
                dict_ = {}
