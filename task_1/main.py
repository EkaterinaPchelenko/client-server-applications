"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт,
осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt,
info_3.txt и формирующий новый «отчетный» файл в формате CSV.

Для этого:

Создать функцию get_data(), в которой в цикле осуществляется перебор файлов
с данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений или другого инструмента извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список. Должно
получиться четыре списка — например, os_prod_list, os_name_list,
os_code_list, os_type_list. В этой же функции создать главный список
для хранения данных отчета — например, main_data — и поместить в него
названия столбцов отчета в виде списка: «Изготовитель системы»,
«Название ОС», «Код продукта», «Тип системы». Значения для этих
столбцов также оформить в виде списка и поместить в файл main_data
(также для каждого файла);

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать получение данных через вызов функции get_data(),
а также сохранение подготовленных данных в соответствующий CSV-файл;

Пример того, что должно получиться:

Изготовитель системы,Название ОС,Код продукта,Тип системы

1,LENOVO,Windows 7,00971-OEM-1982661-00231,x64-based

2,ACER,Windows 10,00971-OEM-1982661-00231,x64-based

3,DELL,Windows 8.1,00971-OEM-1982661-00231,x86-based

Обязательно проверьте, что у вас получается примерно то же самое.

ПРОШУ ВАС НЕ УДАЛЯТЬ СЛУЖЕБНЫЕ ФАЙЛЫ TXT И ИТОГОВЫЙ ФАЙЛ CSV!!!
"""
import csv

files = ['info_1.txt', 'info_2.txt', 'info_3.txt']


def get_data(files):
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    main_data = []
    headers = ["Изготовитель системы", "Название ОС", "Код продукта", "Тип системы"]
    for file in files:
        for line in open(f'{file}', encoding='utf-8'):
            info = line.split(":")
            if info[0] == headers[0]:
                os_prod_list.append(info[1].strip())
            elif info[0] == headers[1]:
                os_name_list.append(info[1].strip())
            elif info[0] == headers[2]:
                os_code_list.append(info[1].strip())
            elif info[0] == headers[3]:
                os_type_list.append(info[1].strip())
    main_data.append(headers)
    for i in range(0, 3):
        my_arr = [i+1, os_prod_list[i], os_name_list[i], os_code_list[i], os_type_list[i]]
        main_data.append(my_arr)
    return main_data

def write_to_csv(files):
    data = get_data(files)
    with open('data_report.csv', 'w', encoding='utf-8') as csv_f:
        csv_f_writer = csv.writer(csv_f)
        for row in data:
            csv_f_writer.writerow(row)


write_to_csv(files)