import logging
import select
import argparse
import socket
import sys
import json
import time

from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, SENDER, RECEIVER, EXIT, RESPONSE_400
from common.utils import get_message, send_message
from my_decorators import log_deco
import logs.server_log_config

from descriptors import Port
from metaclasses import ServerMaker

logger = logging.getLogger('app.server')


@log_deco
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    logger.debug(f'arg_parser: {listen_address, listen_port}')
    return listen_address, listen_port


class Server(metaclass=ServerMaker):
    port = Port()

    def __init__(self, listen_address, listen_port):
        self.address = listen_address
        self.port = listen_port
        self.clients = []
        self.messages = []
        self.names = dict()

    def init_socket(self):
        logger.debug(f'Сервер с адресом {self.address} и портом {self.port} запущен.')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.address, self.port))
        transport.settimeout(0.5)
        self.socket = transport
        self.socket.listen()

    def main_loop(self):
        self.init_socket()

        while True:
            try:
                client, client_addr = self.socket.accept()
            except OSError:
                pass
            else:
                logger.info(f'Установлено соединение с клиентом {client_addr}')
                self.clients.append(client)

            receive_list = []
            send_list = []
            error_list = []

            try:
                if self.clients:
                    receive_list, send_list, error_list = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            if receive_list:
                for cli_with_mes in receive_list:
                    try:
                        self.process_client_message(get_message(cli_with_mes), cli_with_mes,)
                    except:
                        logger.info(f'Клиент {cli_with_mes.getpeername()} отключился от сервера.')
                        self.clients.remove(cli_with_mes)

            for message in self.messages:
                try:
                    self.processing(message, send_list)
                except:
                    logger.error(f'Связь с клиентом {message[RECEIVER]} потеряна.')
                    self.clients.remove(self.names[message[RECEIVER]])
                    del self.names[message[RECEIVER]]
            self.messages.clear()

    def process_client_message(self, message, client):
        logger.debug(f'Сообщение от клиента {message}')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, {RESPONSE: 200})
                logger.debug('Сообщение от клиента корректно')
            else:
                response = RESPONSE_400
                response[ERROR] = 'Такое имя пользователя уже используется.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        elif ACTION in message and message[ACTION] == MESSAGE and \
            RECEIVER in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            return
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            send_message(client, response)
            return

    def processing(self, message, listen_socks):
        if message[RECEIVER] in self.names and self.names[message[RECEIVER]] in listen_socks:
            send_message(self.names[message[RECEIVER]], message)
            logger.info(f'Отправлено соощение. Отправитель: {message[SENDER]}.'
                        f'Получатель: {message[RECEIVER]}')
        elif message[RECEIVER] in self.names and self.names[message[RECEIVER]] not in listen_socks:
            logger.error('Получатель не находится в соккете')
            raise ConnectionError
        else:
            logger.error(f'Пользователь {message[RECEIVER]} не зарегестрирован на сервере.')


def main():
    listen_address, listen_port = arg_parser()
    server = Server(listen_address, listen_port)
    server.main_loop()


if __name__ == '__main__':
    main()
