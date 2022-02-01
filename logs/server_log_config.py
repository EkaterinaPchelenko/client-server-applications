import logging
import os

my_path = os.path.dirname(os.path.abspath(__file__))
my_path = os.path.join(my_path, 'server.log')

logger = logging.getLogger('app.server')

formatter = logging.Formatter('%(asctime)s %(levelname)-10s %(filename)-22s %(message)s')
handler = logging.FileHandler(my_path, encoding='utf8')
logger.setLevel(logging.DEBUG)
handler.setFormatter(formatter)
logger.addHandler(handler)

if __name__ == '__main__':
    logger.debug('debug')
    logger.info('info')
    logger.error('error')
    logger.critical('critical')
