import logging
import select
import socket
import sys
import json
import time

from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT, MESSAGE, MESSAGE_TEXT, SENDER, RECEIVER, EXIT
from common.utils import get_message, send_message
from my_decorators import log_deco
import logs.server_log_config

logger = logging.getLogger('app.server')

@log_deco
def process_client_message(message, mes_list, client, clients, names):
    logger.debug(f'Сообщение от клиента {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message:
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, {RESPONSE: 200})
        else:
            response = {RESPONSE: 400, ERROR: None}
            response[ERROR] = 'Такое имя пользователя уже используется.'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    elif ACTION in message and message[ACTION] == MESSAGE and \
        RECEIVER in message and TIME in message \
        and SENDER in message and MESSAGE_TEXT in message:
        mes_list.append(message)
        return
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    else:
        logger.error(f'Не удалось разобрать сообщение клиента.'
                     f'Неприемлимое состояние параметров.')
        send_message(client,
        {   RESPONSE: 400,
            ERROR: 'Некорректный запрос.'
        })
        return


def processing(message, names, socks):
    if message[RECEIVER] in names and names[message[RECEIVER]] in socks:
        send_message(names[message[RECEIVER]], message)
        logger.info(f'Отправлено соощение. Отправитель: {message[SENDER]}.'
                    f'Получатель: {message[RECEIVER]}')
    elif message[RECEIVER] in names and names[message[RECEIVER]] not in socks:
        logger.error('Получатель не находится в соккете')
        raise ConnectionError
    else:
        logger.error(f'Пользователь {message[RECEIVER]} не зарегестрирован на сервере.')


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
    names = {}

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
                    process_client_message(get_message(cli_with_mes), messages, cli_with_mes, clients, names)
                except:
                    logger.info(f'Клиент {cli_with_mes.getpeername()} отключился от сервера.')
                    clients.remove(cli_with_mes)

        for message in messages:
            try:
                processing(message, names, send_list)
            except Exception:
                logger.error(f'Связь с клиентом {message[RECEIVER]} потеряна.')
                clients.remove(names[message[RECEIVER]])
                del names[message[RECEIVER]]
        messages.clear()


if __name__ == '__main__':
    main()
