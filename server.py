import logging
import select
import socket
import sys
import json
import time

from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, SENDER
from common.utils import get_message, send_message
from my_decorators import log_deco
import logs.server_log_config

logger = logging.getLogger('app.server')

@log_deco
def process_client_message(message, mes_list, client):
    logger.debug(f'Сообщение от клиента {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'ME':
        logger.debug(f'Сообщение {message} от клиента успешно разобрано.')
        send_message(client, {RESPONSE:200})
        return
    elif ACTION in message and message[ACTION] == MESSAGE and TIME in message and MESSAGE_TEXT in message:
        mes_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
    else:
        logger.error(f'Не удалось разобрать сообщение клиента.'
                     f'Неприемлимое состояние параметров.')
        send_message(client,
        {   RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        return


def main():
    try:
        if '-p' in sys.argv:
            server_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            server_port = DEFAULT_PORT
        if server_port < 1024 or server_port > 65535:
            logger.critical(f'Сервер с недопустимым номером порта {server_port}.'
                            f' Допустимое значение порта от 1024 по 65535.')
            raise ValueError
    except IndexError:
        logger.critical(f'Отсутсвует номер порта после параметра -p.')
        # print('Укажите номер порта после параметра -\'p\'.')
        sys.exit(1)
    except ValueError:
        # print(
        #     'Номер порта может быть только от 1024 до 65535.')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            server_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            server_address = ''

    except IndexError:
        logger.critical(f'Отсутсвует адрес порта после параметра -a.')
        # print(
        #     'После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
        sys.exit(1)

    logger.debug(f'Сервер с адресом {server_address} и портом {server_port} запущен.')

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((server_address, server_port))
    transport.settimeout(0.5)
    transport.listen(MAX_CONNECTIONS)

    messages = []
    clients = []

    while True:

        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            logger.info(f'Установлено соединение с клиентом {client_address}')
            clients.append(client)

        receive_list = []
        send_list = []
        error_list = []

        try:
            if clients:
                receive_list, send_list, error_list = select.select(clients, clients, [], 0)
        except OSError:
            pass

        if receive_list:
            for cli_with_mes in receive_list:
                try:
                    process_client_message(get_message(cli_with_mes), messages, cli_with_mes)
                except:
                    logger.info(f'Клиент {cli_with_mes.getpeername()} отключился от сервера.')
                    clients.remove(cli_with_mes)

        if messages and send_list:
            message = {
                ACTION: MESSAGE,
                TIME: time.time(),
                SENDER: messages[0][0],
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for client in send_list:
                try:
                    send_message(client, message)
                except:
                    logger.info(f'Не удалось отправить сообщение. Клиент {client.getpeername()} отключился от сервера.')
                    clients.remove(client)


if __name__ == '__main__':
    main()
