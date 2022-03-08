DEFAULT_PORT = 7777
DEFAULT_IP_ADDRESS = '127.0.0.1'
MAX_CONNECTIONS = 5
MAX_PACKAGE_LENGTH = 1024
ENCODING = 'utf-8'
SERVER_DATABASE = 'sqlite:///server_base.db3'

ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'sender'
RECEIVER = 'receiver'

PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'

MESSAGE = 'message'
MESSAGE_TEXT = 'message text'
EXIT = 'exit'

RESPONSE_200 = {RESPONSE: 200}
RESPONSE_400 = {RESPONSE: 400, ERROR: None}