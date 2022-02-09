import argparse
import logging
import sys
import json
import socket
import time
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import get_message, send_message
import logs.server_log_config

from my_decorators import log_deco


logger = logging.getLogger('app.client')

@log_deco
def create_presence(username='ME'):
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
    print('Для завершения сеанса введите "!!!".')
    message = input('Введите Ваше сообщение: \n')
    if message == '!!!':
        print('Сеанс завершён.')
        logger.info(f'Клиент {username} завершил сеанс.')
        sock.close()
        sys.exit()
    message_info = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: username,
        MESSAGE_TEXT: message
    }
    logger.debug(f'Сформировано сообщение клиента {username}')
    return message_info


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
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    if not 1024 < server_port < 65535:
        logger.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    if client_mode not in ('listen', 'send'):
        logger.critical(f'Указан недопустимый режим работы {client_mode}, '
                        f'допустимые режимы: listen , send')
        sys.exit(1)

    return server_address, server_port, client_mode


def main():
    server_address, server_port, client_params = arg_parser()

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
        # print('Не удалось декодировать сообщение сервера.')
    else:
        if client_params == 'send':
            print('Режим отравки сообщений.')
        if client_params == 'listen':
            print('Режим приёма сообщений.')
        while True:
            if client_params == 'send':
                try:
                    send_message(transport, create_mes(transport))
                except (ConnectionResetError, ConnectionAbortedError, ConnectionError):
                    logger.error(f'Разорвано соединение с сервером {server_address}')
                    sys.exit(1)

            if client_params == 'listen':
                try:
                    message_from_server(get_message(transport))
                except (ConnectionResetError, ConnectionAbortedError, ConnectionError):
                    logger.error(f'Разорвано соединение с сервером {server_address}')
                    sys.exit(1)

if __name__ == '__main__':
    main()

