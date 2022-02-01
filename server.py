import logging
import socket
import sys
import json
from common.variables import ACTION, ACCOUNT_NAME, RESPONSE, MAX_CONNECTIONS, \
    PRESENCE, TIME, USER, ERROR, DEFAULT_PORT
from common.utils import get_message, send_message

import logs.server_log_config

logger = logging.getLogger('app.server')

def process_client_message(message):
    logger.debug(f'Сооющение от клиента {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'ME':
        logger.debug(f'Сообщение {message} от клиента успешно разобрано.')
        return {RESPONSE: 200}
    logger.error(f'Не удалось разобрать сообщение клиента.'
                 f'Неприемлимое состояние параметров.')
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }


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

    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        try:
            client_message = get_message(client)
            print(client_message)
            response = process_client_message(client_message)
            send_message(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            logger.error(f'Принято некорректное сообщение от клиента с адресом {client_address}')
            # print('Принято некорретное сообщение от клиента.')
            client.close()


if __name__ == '__main__':
    main()
