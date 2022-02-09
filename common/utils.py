import json
from common.variables import MAX_PACKAGE_LENGTH, ENCODING

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

    json_message = json.dumps(message)
    enc_message = json_message.encode(ENCODING)
    sock.send(enc_message)
