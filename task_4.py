"""
Задание 4.

Преобразовать слова «разработка», «администрирование», «protocol»,
«standard» из строкового представления в байтовое и выполнить
обратное преобразование (используя методы encode и decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
"""
arr = ['разработка', 'администрирование', 'protocol', 'standard']

for i in arr:
    enc_str = i.encode('utf-8')
    print(enc_str)
    print(type(enc_str))
    dec_str = enc_str.decode('utf-8')
    print(dec_str)
    print(type(dec_str))
    print()