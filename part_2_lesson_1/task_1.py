from ipaddress import ip_address
from subprocess import Popen, PIPE


def host_ping(ip_list):
    available = []
    not_available = []
    for ip_adr in ip_list:
        try:
            address = ip_address(ip_adr)
        except ValueError:
            pass

        process = Popen(['ping', '-c', str(1), '-w', str(3), str(address)], shell=False, stdout=PIPE)
        process.wait()
        if process.returncode == 0:
            available.append(address)
            # print(f'Адресс: {address} доступен.')
        else:
            not_available.append(address)
            # print(f'Адресс: {address} недоступен.')
    return available, not_available


my_list = ['192.168.1.9', '192.168.1.10', 'yandex.ru', '127.0.0.1', '1.2.3.4']
if __name__ == '__main__':
    av, not_av = host_ping(my_list)
    print(f'Доступные адресса: {av}, недоступные: {not_av}')