import os
import pandas as pd


class PriceMachine:

    def __init__(self):
        # self.data = []
        # self.result = ''
        # self.name_length = 0
        self.prices = pd.DataFrame(columns=['№', 'Наименование', 'Цена', 'Вес', 'Цена за кг.', 'Файл'])

    def load_prices(self, file_path=os.path.dirname(os.path.realpath(__file__))):
        # по умолчанию будем искать файлы в директории, где находиться этот файл
        # в цикле перебираем файлы
        for file in os.listdir(file_path):
            if file.endswith('.csv') and 'price' in file:
                print(f'чтение данных из файла {file}')
                # загружаем сразу в PANDAS дата-фрейм
                df_from_file = pd.read_csv(os.path.join(file_path, file), encoding='utf-8')
                # отправляем на корректировку -> получаем исправленный фрейм данных
                new_df = self._search_product_price_weight(df_from_file)
                # добавляем столбец с названием файла
                new_df['Файл'] = file.split('.')[0]
                # объединяем в общий дата-фрейм, который инициирован в __init__
                self.prices = pd.concat([self.prices, new_df])
        # Добавить столбец 'Цена за кг.' = round(new_df['Цена'] / new_df['Вес'], 2)
        # self.prices['Цена за кг.'] = round(self.prices['Цена'] / self.prices['Вес'], 2)
        self.prices['Цена за кг.'] = self.prices['Цена'] / self.prices['Вес']
        # Сортируем по столбцу 'Цена за кг.'
        self.prices.sort_values(by='Цена за кг.', ascending=True, inplace=True)
        # сбрасываем индексацию
        self.prices = self.prices.reset_index(drop=True)
        # Перезаписываем столбец с нумерацией
        self.prices['№'] = range(1, len(self.prices) + 1)
        # self.prices.insert(1, '№', range(1, len(self.prices) + 1))
        return self.prices

    def _search_product_price_weight(self, date_frame):
        """
        Правим дата-фрейм:
            полезные столбцы - переименовываем
            ненужные столбцы - удаляем
        :param date_frame:
        :return: PANDAS date_frame
        """
        # удаление столбцов без названия
        date_frame = date_frame.dropna(how="all", axis=1)
        for i, header in enumerate(date_frame):
            """Перебираем столбцы, ищем по названию, переименовываем"""
            if header.lower() in ['название', 'продукт', 'товар', 'наименование']:
                date_frame = date_frame.rename(columns={header: 'Наименование'})
            elif header.lower() in ['цена', 'розница']:
                date_frame = date_frame.rename(columns={header: 'Цена'})
            elif header.lower() in ['вес', 'масса', 'фасовка']:
                date_frame = date_frame.rename(columns={header: 'Вес'})
            else:
                # Если столбец не нужный - дропаем (удаляем) его
                date_frame = date_frame.drop(columns=[header])
        return date_frame

    def export_to_html(self, df, file_name='output.html'):
        """
        Заполняем таблицу в HTML документе
        и сохраняем в файл
        :param df:
        :param file_name
        :return:
        """
        result = '''<!DOCTYPE html>
            <html>
            <head>
                <title>Позиции продуктов</title>
                    <style>
                        table {
                            border-spacing: 16px 0px; /* Расстояние между ячейками */ 
                        }
                    </style>
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
        for i in range(len(df)):
            result += '<tr>'
            result += f'<td align="right"> {df["№"].values[i]}</td>'
            result += f'<td> {df["Наименование"].values[i]}</td>'
            result += f'<td align="right"> {df["Цена"].values[i]}</td>'
            result += f'<td align="right"> {df["Вес"].values[i]}</td>'
            result += f'<td> {df["Файл"].values[i]}</td>'
            result += f'<td align="right"> {round(df["Цена за кг."].values[i],1)}</td>'
            result += '</tr>\n'
        result += '\t</table>\n'
        result += '</body>'
        with open(file_name, 'w') as f:
            f.write(result)

    def find_text(self, search_text):
        """
        Поиск данных в получившемся дата-фрейме и вывод на консоль
        если данных по запросу не нашлось - выводим запрос по умолчанию
        для примера (и для проверок при написании этой программы)
        :param search_text:
        :return:
        """
        matches = self.prices[self.prices['Наименование'].str.contains(search_text, case=False)]
        if len(matches):
            self.export_to_html(df=matches, file_name='output.html')
            return matches
        else:
            print(f'Продукта с наименованием: {search_text}, не найдено. '
                  f'Для примера выводим данные по запросу: "Пелядь крупная х/к потр"')
            return self.find_text('Пелядь крупная х/к потр')


if __name__ == "__main__":
    pm = PriceMachine()
    # Программа должна загрузить данные из всех прайс-листов
    pm.load_prices()
    print('Все файлы прочитаны')
    pm.export_to_html(file_name='output.html', df=pm.find_text(''))
    print('Данные выгружены в html файл: output.html\n'
          '\nКоманда - "all" - позволит получить полный список позиций в виде таблицы'
          '\nКоманда - "exit" - завершить работу программы'
          '\nДля вывода данных по продукту - ')
    # Предоставить интерфейс для поиска товара по фрагменту названия с сортировкой по цене за килограмм.
    while True:
        search_text = input('\nВведите наименование продукта: ')
        if search_text.lower().strip() == "exit":
            break
        elif search_text == "all":
            print(pm.prices)
        else:
            print(pm.find_text(search_text))
    print('Работа завершена.')
