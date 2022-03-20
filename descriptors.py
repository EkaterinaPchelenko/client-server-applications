import ipaddress
import logging
logger = logging.getLogger('app.server')


class Port:
    def __set__(self, instance, value):
        if not 1024 < value < 65535:
            logger.critical(f'Сервер с недопустимым номером порта {value}.'
                            f' Допустимое значение порта от 1024 по 65535.')
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class Host:
    def __set__(self, instance, value):
        if value:
            try:
                ip = ipaddress.ip_address(value)
            except ValueError as e:
                logger.critical(f'Некорректный ip адресс {e}')
                exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


















