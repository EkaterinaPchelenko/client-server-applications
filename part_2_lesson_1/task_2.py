from ipaddress import ip_address

from task_1 import host_ping


def host_range_ping():
    _range = input('Задайте диапазон ip-адрессов через пробел (Пример: 1.1.1.1 1.1.1.3): ').split(' ')
    _from, till = ip_address(_range[0]), ip_address(_range[1])
    my_list = []
    while _from <= till:
        my_list.append(_from)
        _from += 1
    return host_ping(my_list)

if __name__ == '__main__':
    av, not_av = host_range_ping()
    print(f'Доступные адресса: {av}, недоступные: {not_av}')

