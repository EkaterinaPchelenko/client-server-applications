import unittest

from client import create_presence, process_ans
from common.variables import ACTION, USER, ACCOUNT_NAME, PRESENCE, TIME, RESPONSE, ERROR

class TestClient(unittest.TestCase):
    def test_create_presence(self):
        info = create_presence()
        info[TIME] = 10
        self.assertEqual(info, {ACTION:PRESENCE, TIME:10, USER:{ACCOUNT_NAME:'ME'}})

    def test_process_ans(self):
        message = {RESPONSE: 200}
        self.assertEqual(process_ans(message), '200 : OK')

    def test_process_ans_err(self):
        message = {RESPONSE: 400, ERROR: 'Bad Request'}
        self.assertEqual(process_ans(message), '400 : Bad Request')

    def test_process_ans_is_response_in_message(self):
        message = {USER: 'ME'}
        self.assertRaises(ValueError, process_ans, message)

