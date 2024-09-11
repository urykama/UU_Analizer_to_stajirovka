import os
import re
import pandas as pd


class PriceMachine:

    def __init__(self):
        # self.data = []
        # self.result = ''
        # self.name_length = 0
        self.prices = pd.DataFrame(columns=['№', 'Наименование', 'Цена', 'Вес', 'Цена за кг.', 'Файл'])

    def load_prices(self, file_path=os.path.dirname(os.path.realpath(__file__))):
        for file in os.listdir(file_path):
            if file.endswith('.csv') and 'price' in file:
                print(f'чтение данных из файла {file}')
                df = pd.read_csv(os.path.join(file_path, file), sep=',', header=None, encoding='utf-8')
                df = df.dropna(how="all", axis=1)
                df = df.reset_index(drop=True)
                col_product, col_price, col_weight = self._search_product_price_weight(df)
                new_df = pd.DataFrame(columns=['№', 'Наименование', 'Цена', 'Вес', 'Цена за кг.', 'Файл'])
                new_df['№'] = range(1, len(new_df) + 1)
                new_df['Наименование'] = col_product
                new_df['Цена'] = col_price
                new_df['Вес'] = col_weight
                new_df['Файл'] = file.split('.')[0]
                new_df = new_df.drop(index=0)
                new_df = new_df.reset_index(drop=True)
                new_df['Цена'] = new_df['Цена'].astype(float)
                new_df['Вес'] = new_df['Вес'].astype(float)
                new_df['Цена за кг.'] = round(new_df['Цена'] / new_df['Вес'], 2)
                new_df.dropna(axis=1, how='all', inplace=True)
                self.prices.dropna(axis=1, how='all', inplace=True)
                self.prices = pd.concat([self.prices, new_df])
        self.prices.sort_values(by='Цена за кг.', ascending=True, inplace=True)
        self.prices = self.prices.reset_index(drop=True)
        self.prices['№'] = range(1, len(self.prices) + 1)
        return self.prices

    def _search_product_price_weight(self, headers):
        for i, header in enumerate(headers):
            if re.match(r'^название|^товар|^наименование|^продукт$', headers[header][0], re.IGNORECASE):
                col_product = headers[header]
            elif re.match(r'^цена|^розница$', headers[header][0], re.IGNORECASE):
                col_price = headers[header]
            elif re.match(r'^вес|^масса|^фасовка$', headers[header][0], re.IGNORECASE):
                col_weight = headers[header]
        return col_product, col_price, col_weight

    def export_to_html(self, fname='output.html'):
        result = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''
        for i in range(len(self.prices)):
            result += '<tr>'
            result += f'<td>{self.prices["№"].values[i]}</td>'
            result += f'<td>{self.prices["Наименование"].values[i]}</td>'
            result += f'<td>{self.prices["Цена"].values[i]}</td>'
            result += f'<td>{self.prices["Вес"].values[i]}</td>'
            result += f'<td>{self.prices["Файл"].values[i]}</td>'
            result += f'<td>{self.prices["Цена за кг."].values[i]}</td>'
            result += '</tr>'
        result += '</table>'
        with open(fname, 'w') as f:
            f.write(result)

    def find_text(self, search_text):
        matches = self.prices[self.prices['Наименование'].str.contains(search_text, case=False)]
        if len(matches):
            return matches
        else:
            print(f'Продукта с наименованием: {search_text}, не найдено. '
                  f'Для примера выводим данные по запросу: "Пелядь крупная х/к потр"')
            return self.find_text('Пелядь крупная х/к потр')


if __name__ == "__main__":
    pm = PriceMachine()
    pm.load_prices()
    print('Все файлы прочитаны')
    pm.export_to_html('output.html')
    print('Данные выгружены в html файл: output.html')
    print('\nКоманда - "all" - позволит получить полный список позиций в виде таблицы')
    print('Команда - "exit" - завершить работу программы')
    print('Для вывода данных по продукту - ')

    while True:
        search_text = input('\nВведите наименование продукта: ')
        if search_text.lower().strip() == "exit":
            break
        elif search_text == "all":
            print(pm.prices['result'])
        else:
            print(pm.find_text(search_text))
    print('Работа завершена.')
