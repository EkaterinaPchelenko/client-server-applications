import logging
logger = logging.getLogger('app.server')


class Port:
    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, value):
        if not 1024 < value < 65535:
            logger.critical(f'Сервер с недопустимым номером порта {value}.'
                            f' Допустимое значение порта от 1024 по 65535.')
            exit(1)
        instance.__dict__[self.name] = value
