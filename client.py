import argparse
import logging
import sys
import json
import socket
import threading
import time

from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, SENDER, RECEIVER, EXIT
from common.utils import get_message, send_message
import logs.server_log_config

from metaclasses import ClientMaker


from my_decorators import log_deco


logger = logging.getLogger('app.client')


class ClientSender(threading.Thread, metaclass=ClientMaker):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def create_mes(self):
        receiver = input('Введите имя получателя: ')
        message = input('Введите Ваше сообщение: \n')
        message_info = {
            ACTION: MESSAGE,
            RECEIVER: receiver,
            TIME: time.time(),
            SENDER: self.account_name,
            MESSAGE_TEXT: message
        }
        logger.debug(f'Сформировано сообщение клиента {self.account_name}')

        try:
            send_message(self.sock, message_info)
            logger.info(f'Отправлено сообщение для пользовтаеля {receiver}')
        except:
            logger.critical('Соединение с сервером разорвано!')
            sys.exit(1)


    def functional(self):
        self.commands()
        logger.info('Вход в functional')
        while True:
            command = input('Введите комманду из предложенных: ')
            if command == 'message':
                self.create_mes()
            elif command == 'help':
                self.commands()
            elif command == 'exit':
                send_message(self.sock, self.exit_message())
                print('Выполняется выход из программы.')
                time.sleep(0.5)
                break
            else:
                print('Неправильно введена команда. Попробуйте ещё раз.'
                      ' Введите help, чтобы посмотреть перечень команд.')


    def commands(self):
        print('Команды:')
        print('message - отправить сообщение.')
        print('help - вывести подсказки по командам.')
        print('exit - выход.')

    def exit_message(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }


class ClientReader(threading.Thread, metaclass=ClientMaker):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def message_from_server(self):
        while True:
            try:
                message = get_message(self.sock)
                if ACTION in message and message[ACTION] == MESSAGE and \
                        SENDER in message and RECEIVER in message \
                        and MESSAGE_TEXT in message and message[RECEIVER] == self.account_name:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                          f'\n{message[MESSAGE_TEXT]}')
                    logger.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                                f'\n{message[MESSAGE_TEXT]}')
                else:
                    logger.error(f'Получено некорректное сообщение с сервера: {message}')

            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                logger.critical(f'Потеряно соединение с сервером.')
                break


@log_deco
def create_presence(account_name):
    info = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    logger.info(f'Получено сообщение для пользователя {account_name}')
    return info


@log_deco
def process_ans(message):
    logger.debug(f'Сообщение от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            # logger.debug(f'Сообщение {message} успешно разобрано')
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    logger.error(f'Не удалось разобрать сообщение {message}.'
                 f'Параметр {RESPONSE} отсутствует в сообщении.')
    raise ReqFieldMissingError(RESPONSE)


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
        exit(1)

    return server_address, server_port, username


def main():
    server_address, server_port, client_name = arg_parser()
    if not client_name:
        client_name = input('Введите имя пользователя: ')
    else:
        print(f'Клиентский модуль запущен с именем: {client_name}')

    logger.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address} , порт: {server_port}, имя пользователя: {client_name}')

    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        message = create_presence(client_name)
        send_message(transport, message)
        answer = process_ans(get_message(transport))
        logger.info(f'Принято сообщение от сервера: {answer}')
        # print(answer)
    except json.JSONDecodeError:
        logger.error('Не удалось декодировать полученную Json строку.')
        exit(1)
    except ServerError as error:
        logger.error(f'При установке соединения сервер вернул ошибку: {error.text}')
        exit(1)
    except ReqMissingFieldError as missing_error:
        logger.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        logger.critical(
            f'Не удалось подключиться к серверу {server_address}:{server_port}, конечный компьютер отверг запрос на подключение.')
        exit(1)
    else:
        receiver = ClientReader(client_name, transport)
        receiver.daemon = True
        receiver.start()

        interface = ClientSender(client_name, transport)
        interface.daemon = True
        interface.start()

        logger.debug('Запуск процессов.')

        while True:
            time.sleep(1)
            if receiver.is_alive() and interface.is_alive():
                continue
            break


class ServerError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class ReqMissingFieldError(Exception):
    def __init__(self, field):
        self.field = field

    def __str__(self):
        return f'В принятом словаре отсутствует обязательное поле {self.field}.'


class ReqFieldMissingError(Exception):
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'В принятом словаре отсутствует обязательное поле {self.missing_field}.'


if __name__ == '__main__':
    main()

