from tabulate import tabulate

from task_2 import host_range_ping


def host_range_ping_tab():
    available, not_available = host_range_ping()
    my_dict = {'reachable': available, 'unreachable': not_available}
    print(tabulate(my_dict, headers='keys', tablefmt='grid', stralign='center'))


if __name__ == '__main__':
    host_range_ping_tab()