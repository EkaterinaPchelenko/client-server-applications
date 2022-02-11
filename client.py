import argparse
import logging
import sys
import json
import socket
import threading
import time
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, SENDER, RECEIVER
from common.utils import get_message, send_message
import logs.server_log_config

from my_decorators import log_deco


logger = logging.getLogger('app.client')

@log_deco
def create_presence(username):
    info = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: username
        }
    }
    logger.info(f'Получено сообщение для пользователя {username}')
    return info


@log_deco
def message_from_server(message):
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        print(f'Получено сообщение от пользователя '
              f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        logger.info(f'Получено сообщение от пользователя '
                    f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        logger.error(f'Получено некорректное сообщение с сервера: {message}')


@log_deco
def create_mes(sock, username='ME'):
    receiver = input('Введите имя получателя: ')
    message = input('Введите Ваше сообщение: \n')
    message_info = {
        ACTION: MESSAGE,
        RECEIVER: receiver,
        TIME: time.time(),
        ACCOUNT_NAME: username,
        MESSAGE_TEXT: message
    }
    logger.debug(f'Сформировано сообщение клиента {username}')

    try:
        send_message(sock, message_info)
        logger.info(f'Отправлено сообщение для пользовтаеля {receiver}')
    except:
        logger.critical('Соединение с сервером разорвано!')
        sys.exit(1)

def commands():
    print('Команды:')
    print('message - отправить сообщение.')
    print('help - вывести подсказки по командам.')
    print('exit - выход.')


def functional(sock, username):
    while True:
        command = input('Введите комманду из предложенных: ')
        if command == 'message':
            create_mes(sock, username)
        if command == 'help':
            commands()
        if command == 'exit':
            print('Выполняется выход из программы.')
            time.sleep(0.5)
            break
        else:
            print('Неправильно введена команда. Попробуйте ещё раз.'
                  ' Введите help, чтобы посмотреть перечень команд.')


@log_deco
def process_ans(message):
    logger.debug(f'Сообщение от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            logger.debug(f'Сообщение {message} успешно разобрано')
            return '200 : OK'
        logger.error(f'Не удалось разобрать сообщение {message}.'
                     f'Неверный {RESPONSE}, дупустимое значение - 200')
        return f'400 : {message[ERROR]}'
    logger.error(f'Не удалось разобрать сообщение {message}.'
                 f'Параметр {RESPONSE} отсутствует в сообщении.')
    raise ValueError


@log_deco
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    username = namespace.name

    if not 1024 < server_port < 65535:
        logger.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    return server_address, server_port, username


def main():
    server_address, server_port, username = arg_parser()
    if not username:
        username = input('Введите имя пользователя: ')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        message = create_presence()
        send_message(transport, message)
        answer = process_ans(get_message(transport))
        logger.info(f'Принято сообщение от сервера: {answer}')
        # print(answer)
    except (ValueError, json.JSONDecodeError):
        logger.error('Не удалось декодировать сообщение сервера.')
        sys.exit(1)
        # print('Не удалось декодировать сообщение сервера.')

    else:
        receiver = threading.Thread(target=message_from_server, args=(transport, username))
        receiver.daemon = True
        receiver.start()

        interface = threading.Thread(target=functional, args=(transport, username))
        interface.daemon = True
        interface.start()

        logger.debug('Запуск процессов.')

        while True:
            time.sleep(1)
            if receiver.is_alive() and interface.is_alive():
                continue
            break



if __name__ == '__main__':
    main()

