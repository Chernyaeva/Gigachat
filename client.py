from socket import *
import time
from datetime import datetime
import sys, getopt  # to work with command line arguments
import json
import logging
import Logs.config_client_log
from decorators import log
from threading import Thread

#initialyze logger
logger = logging.getLogger('client')



@log(logger)
def send_presence(mysocket, user_name):
    presense_message = {
    "action": "presence",
    "time": time.mktime(datetime.now().timetuple()),
    "type": "status",
    "user": {
        "account_name": user_name,
        "status": "I'm still alive!"
    }
   }
    presense_message['time'] = time.mktime(datetime.now().timetuple())
    msg = json.dumps(presense_message)
    mysocket.send(msg.encode('utf-8'))


def parse_cmd_args(argv):
   # Parse command line arguments for port, address, username
    address = 'localhost'
    port = 7777
    username = ''
    opts, args = getopt.getopt(argv,"ha:p:",["address=","port="])
    for opt, arg in opts:
      if opt == '-h':
         print ('client.py /n -a <accepted client address. default - all> /n -p <listen port. default 7777> /n -n Username')
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
    data = mysocket.recv(1000)
    logger.info('New data received from server %s',data)
    return json.loads(data.decode('utf-8'))     


def receive_handler(mysocket):
   while True:
      msg_dict = receive_message(mysocket)
      print(f'{datetime.fromtimestamp(float(msg_dict["time"]))} {msg_dict["from"]}: {msg_dict["message"]}')

@log(logger)
def send_message(mysocket, username, recipient, message_text):
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

def main(argv):
    # Parse command line arguments for port and address
    address, port, username = parse_cmd_args(argv)
    # Make and bind socket
    s = socket(AF_INET, SOCK_STREAM) # Создать сокет TCP
    try:
      s.connect((address, port)) # Соединиться с сервером
    except:
      logger.error('Could not connect to server %s:%s', address, port)
      return   
    if username == '':
      username = input('Your name: ')
    send_presence(s, username)
    print(f'Hello, {username}! Type recipient name and you message. Type quit to quit the app')
    receive_thread =  Thread(target=receive_handler, args=(s, ))
    receive_thread.daemon = True
    receive_thread.start()
    while True:
         recipient = input('Recipient name: ')
         message = input('Your message: ')
         if recipient == 'quit' or message == 'quit':
            sys.exit()
         send_message(s, username, recipient, message)
       

if __name__ == "__main__":
   main(sys.argv[1:])

