import os
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
                df_from_file = pd.read_csv(os.path.join(file_path, file), encoding='utf-8')
                new_df = self._search_product_price_weight(df_from_file)
                new_df['Файл'] = file.split('.')[0]
                self.prices = pd.concat([self.prices, new_df])
        # Добавить столбец 'Цена за кг.' = round(new_df['Цена'] / new_df['Вес'], 2)
        self.prices['Цена за кг.'] = round(self.prices['Цена'] / self.prices['Вес'], 2)
        self.prices.sort_values(by='Цена за кг.', ascending=True, inplace=True)
        self.prices = self.prices.reset_index(drop=True)
        self.prices['№'] = range(1, len(self.prices) + 1)
        # self.prices.insert(1, '№', range(1, len(self.prices) + 1))
        return self.prices

    def _search_product_price_weight(self, headers):
        headers = headers.dropna(how="all", axis=1)
        for i, header in enumerate(headers):
            if header.lower() in ['название', 'продукт', 'товар', 'наименование']:
                headers = headers.rename(columns={header: 'Наименование'})
            elif header.lower() in ['цена', 'розница']:
                headers = headers.rename(columns={header: 'Цена'})
            elif header.lower() in ['вес', 'масса', 'фасовка']:
                headers = headers.rename(columns={header: 'Вес'})
            else:
                headers = headers.drop(columns=[header])
        return headers

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
            print(pm.prices)
        else:
            print(pm.find_text(search_text))
    print('Работа завершена.')
