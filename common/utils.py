import json
import logging

from common.variables import MAX_PACKAGE_LENGTH, ENCODING

logger = logging.getLogger('app.server')

def get_message(client):
    enc_response = client.recv(MAX_PACKAGE_LENGTH)
    if type(enc_response) == bytes:
        json_resp = enc_response.decode(ENCODING)
        response = json.loads(json_resp)
        if type(response) == dict:
            return response
        raise ValueError
    raise ValueError


class NonDictInputError:
    pass


def send_message(sock, message):
    logger.debug('SEND MESSAGE')
    json_message = json.dumps(message)
    enc_message = json_message.encode(ENCODING)
    sock.send(enc_message)
