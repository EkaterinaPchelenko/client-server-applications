"""
3. Задание на закрепление знаний по модулю yaml.
 Написать скрипт, автоматизирующий сохранение данных
 в файле YAML-формата.
Для этого:

Подготовить данные для записи в виде словаря, в котором
первому ключу соответствует список, второму — целое число,
третьему — вложенный словарь, где значение каждого ключа —
это целое число с юникод-символом, отсутствующим в кодировке
ASCII(например, €);

Реализовать сохранение данных в файл формата YAML — например,
в файл file.yaml. При этом обеспечить стилизацию файла с помощью
параметра default_flow_style, а также установить возможность работы
с юникодом: allow_unicode = True;

Реализовать считывание данных из созданного файла и проверить,
совпадают ли они с исходными.
"""
import yaml
from yaml import SafeLoader

my_dict = {
    'products': ['processors', 'motherboards', 'screens'],
    'amount': 100,
    'price': {
        'processors': '200€',
        'motherboards': '150€',
        'screens': '100€'
    }
}

with open('file.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(my_dict, file, default_flow_style=False, allow_unicode=True)

with open('file.yaml', 'r', encoding='utf-8') as file:
    info = yaml.load(file, Loader=SafeLoader)

if info == my_dict:
    print('Данные совпадают')



