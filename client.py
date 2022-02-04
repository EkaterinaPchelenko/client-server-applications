import logging
import sys
import json
import socket
import time
from common.variables import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, \
    RESPONSE, ERROR, DEFAULT_IP_ADDRESS, DEFAULT_PORT
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


def main():
    try:
        client_address = sys.argv[1]
        client_port = int(sys.argv[2])
        if client_port < 1024 or client_port > 65535:
            logger.critical(f'Клиент с недопустимым номером порта {client_port}.'
                            f' Допустимое значение порта от 1024 по 65535.')
            raise ValueError
    except IndexError:
        client_address = DEFAULT_IP_ADDRESS
        client_port = DEFAULT_PORT
    except ValueError:
        # print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.connect((client_address, client_port))
    message = create_presence()
    send_message(transport, message)
    try:
        answer = process_ans(get_message(transport))
        logger.info(f'Принято сообщение от сервера: {answer}')
        print(answer)
    except (ValueError, json.JSONDecodeError):
        logger.error('Не удалось декодировать сообщение сервера.')
        # print('Не удалось декодировать сообщение сервера.')

if __name__ == '__main__':
    main()

