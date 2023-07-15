from socket import *
import time
from datetime import datetime
import sys
import getopt
import json
import logging
from threading import Thread

import hashlib
import binascii

import Logs.config_client_log
from decorators import log
from metaclasses import ClientVerifier
from client_db import ClientStorage

# initialyze logger
logger = logging.getLogger('client')


class ClientSender(Thread, metaclass=ClientVerifier):
    '''Handles commands from user and sends messages to server'''

    def __init__(self, account_name, sock, storage):
        self.account_name = account_name
        self.sock = sock
        self.storage = storage
        super().__init__()
        request_contacts(self.sock, self.account_name)

    def create_message(self):
        '''Asks user to enter message and recepient and sends message to server'''
        recipient = input('Recipient name: ')
        message = input('Your message: ')
        try:
            send_message(self.sock, self.account_name, recipient, message)
            self.storage.save_message(self.account_name, recipient, message)
            logger.info(f'Отправлено сообщение для пользователя {recipient}')
        except BaseException:
            logger.critical('Потеряно соединение с сервером.')
            exit(1)

    def run(self):
        '''Handles commands from user and sends command messages to server'''
        print(
            f'Hello, {self.account_name}! Type m to send message, a to add contact, or e to exit the app.')
        while True:
            command = input()
            if command == 'message' or command == 'm':
                self.create_message()
            elif command == 'add' or command == 'a':
                contact_name = input("Write contact name: ")
                add_contact(self.sock, self.account_name, contact_name)
            elif command == 'exit' or command == 'e':
                try:
                    send_exit(self.sock, self.account_name)
                except BaseException:
                    pass
                print('Завершение соединения.')
                logger.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            else:
                print(
                    'Unsupported command. Type m to send message or e to exit the app.')


class ClientReader(Thread, metaclass=ClientVerifier):
    '''Handles receiving messages from server and prints them in console'''

    def __init__(self, account_name, sock, storage):
        self.account_name = account_name
        self.sock = sock
        self.storage = storage
        print(f'ClientReader: {self.storage}')
        print(self.storage.get_history())
        super().__init__()

    def run(self):
        '''Main loop. Receives and parses messages from server'''
        while True:
            try:
                message = receive_message(self.sock)
                if "action" in message and message["action"] == 'msg' and "from" in message and 'message' in message \
                        and 'to' in message and message['to'] == self.account_name:
                    print(
                        f'{datetime.fromtimestamp(float(message["time"]))} {message["from"]}: {message["message"]}')
                    self.storage.save_message(
                        message["from"], self.account_name, message["message"])
                    logger.info(
                        f'Получено сообщение от пользователя {message["from"]}:\n{message["message"]}')
                elif "response" in message and message["response"] == "202":
                    logger.info(
                        f'Received list of contacts from server: {message["alert"]}')
                    for contact in message["alert"]:
                        self.storage.save_contact(contact)
                else:
                    logger.error(
                        f'Получено некорректное сообщение с сервера: {message}')
            except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
                logger.critical(f'Потеряно соединение с сервером.')
                break


def send_presence(mysocket, user_name, password_hash):
    '''Generates presence message and sends it to server'''
    presense_message = {
        "action": "presence",
        "time": time.mktime(datetime.now().timetuple()),
        "type": "status",
        "user": {
            "account_name": user_name,
            "password_hash": password_hash
        }
    }
    msg = json.dumps(presense_message)
    mysocket.send(msg.encode('utf-8'))


def request_contacts(mysocket, user_name):
    '''Generates request contacts message and sends it to server'''
    request_message = {
        "action": "get_contacts",
        "time": time.mktime(datetime.now().timetuple()),
        "user_login": user_name,
    }
    msg = json.dumps(request_message)
    mysocket.send(msg.encode('utf-8'))


def add_contact(mysocket, user_name, contact_name):
    '''Generates add contacts message and sends it to server'''
    request_message = {
        "action": "add_contact",
        "user_id": contact_name,
        "time": time.mktime(datetime.now().timetuple()),
        "user_login": user_name,
    }
    msg = json.dumps(request_message)
    mysocket.send(msg.encode('utf-8'))


def parse_cmd_args(argv):
    '''Parses command line arguments for port, address, username'''
    address = 'localhost'
    port = 7777
    username = ''
    opts, args = getopt.getopt(argv, "ha:p:", ["address=", "port="])
    for opt, arg in opts:
        if opt == '-h':
            print('client.py /n -a <accepted client address. default - all> /n -p <listen port. default 7777> /n -n Username')
            sys.exit()
        elif opt in ("-a", "--address"):
            address = arg
        elif opt in ("-p", "--port"):
            port = arg
        elif opt in ("-n", "--name"):
            username = arg
    logger.info('Client started with parameters -p %s -a %s', port, address)
    return address, port, username


@log(logger)
def receive_message(mysocket):
    '''Receives message from server and returns it as dictionary'''
    data = mysocket.recv(1000)
    logger.info('New data received from server %s', data)
    return json.loads(data.decode('utf-8'))


def send_message(mysocket, username, recipient, message_text):
    '''Assambles message to another user and sends it to server'''
    message = {
        "action": "msg",
        "encoding": "utf-8",
    }
    message['time'] = time.mktime(datetime.now().timetuple())
    message['from'] = username
    message['to'] = recipient
    message['message'] = message_text
    msg = json.dumps(message)
    mysocket.send(msg.encode('utf-8'))


def send_exit(mysocket, username):
    '''Gererates exit message and sends it to server'''
    message = {
        "action": "exit",
        'time': time.mktime(datetime.now().timetuple()),
        'account_name': username
    }
    msg = json.dumps(message)
    mysocket.send(msg.encode('utf-8'))


def main(argv):
    # Initialyze databse
    storage = ClientStorage()
    # Parse command line arguments for port and address
    address, port, username = parse_cmd_args(argv)
    # Make and bind socket
    s = socket(AF_INET, SOCK_STREAM)  # Create TCP socket
    try:
        s.connect((address, port))  # Connect to server
    except BaseException:
        logger.error('Could not connect to server %s:%s', address, port)
        exit(1)
    if username == '':
        username = input('Your name: ')
    password = input('Your password: ')
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        username.encode('utf-8'),
        100000)
    send_presence(s, username, binascii.hexlify(password_hash).decode('utf-8'))
    time.sleep(1)
    # Если соединение с сервером установлено корректно, запускаем клиенский
    # процесс приёма сообщний
    module_reciver = ClientReader(username, s, storage)
    module_reciver.daemon = True
    module_reciver.start()
    # затем запускаем отправку сообщений и взаимодействие с пользователем.
    module_sender = ClientSender(username, s, storage)
    module_sender.daemon = True
    module_sender.start()
    logger.debug('Запущены процессы')
    # Watchdog основной цикл, если один из потоков завершён, то значит или потеряно соединение или пользователь
    # ввёл exit. Поскольку все события обработываются в потоках, достаточно
    # просто завершить цикл.
    while True:
        time.sleep(1)
        if module_reciver.is_alive() and module_sender.is_alive():
            continue
        break


if __name__ == "__main__":
    main(sys.argv[1:])
