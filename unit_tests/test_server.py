import unittest

from common.variables import ACTION, USER, ACCOUNT_NAME, PRESENCE, TIME, RESPONSE, ERROR
from server import process_client_message


class TestServer(unittest.TestCase):
    error = {RESPONSE: 400, ERROR: 'Bad Request'}
    response = {RESPONSE: 200}
    def test_process_message_no_action(self):
        message = {TIME: 10, USER:{ACCOUNT_NAME: 'ME'}}
        self.assertEqual(process_client_message(message), self.error)

    def test_process_message_wrong_action(self):
        message = {ACTION: 'wrong action', TIME: 10, USER:{ACCOUNT_NAME: 'ME'}}
        self.assertEqual(process_client_message(message), self.error)

    def test_process_message_no_time(self):
        message = {ACTION: PRESENCE, USER:{ACCOUNT_NAME: 'ME'}}
        self.assertEqual(process_client_message(message), self.error)

    def test_process_message_no_user(self):
        message = {TIME: 10, ACTION: PRESENCE}
        self.assertEqual(process_client_message(message), self.error)

    def test_process_message_wrong_accountname(self):
        message = {ACTION: PRESENCE, TIME: 10, USER:{ACCOUNT_NAME: 'wrong name'}}
        self.assertEqual(process_client_message(message), self.error)

    def test_process_message_everything_okay(self):
        message = {ACTION: PRESENCE, TIME: 10, USER:{ACCOUNT_NAME: 'ME'}}
        self.assertEqual(process_client_message(message), self.response)

