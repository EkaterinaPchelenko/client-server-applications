"""
Задание 5.

Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.

Подсказки:
--- используйте модуль chardet, иначе задание не засчитается!!!
"""

import subprocess

import chardet
arr = ['yandex.ru', 'youtube.com']

for j in arr:
    info = ['ping', j]

    my_ping = subprocess.Popen(info, stdout=subprocess.PIPE)
    for i in my_ping.stdout:
        res = chardet.detect(i)
        line = i.decode(res['encoding']).encode('utf-8')
        print(line.decode('utf-8'))

