import sys
import logging
import logs.client_log_config
import logs.server_log_config
import traceback
import inspect

if sys.argv[0].find('client') == -1:
    logger = logging.getLogger('app.server')
else:
    logger = logging.getLogger('app.client')


def log_deco(func):
    def log_wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        logger.debug(f'Вызвана функция {func.__name__} с аргументами {args, kwargs}.'
                     f'Вызов произведён из функции {traceback.format_stack()[0].strip().split()[-1]}')
        return res
    return log_wrapper
