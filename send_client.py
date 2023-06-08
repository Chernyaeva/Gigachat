from socket import *
import time
from datetime import datetime
import sys, getopt  # to work with command line arguments
import json
import logging
import Logs.config_client_log
from decorators import log

#initialyze logger
logger = logging.getLogger('client')


message = {
    "action": "msg",
    "time": 0.0,
    "to": "account_name",
    "from": "account_name",
    "encoding": "utf-8",
    "message": "message"
}


@log(logger)
def send_message(mysocket, username, message_text):
    message['time'] = time.mktime(datetime.now().timetuple())
    message['from'] = username
    message['message'] = message_text
    msg = json.dumps(message)
    mysocket.send(msg.encode('utf-8'))


def main(argv):
    # Parse command line arguments for port and address
    address = 'localhost'
    port = 7777
    opts, args = getopt.getopt(argv,"ha:p:",["address=","port="])
    for opt, arg in opts:
      if opt == '-h':
         print ('client.py -a <accepted client address. default - all> -p <listen port. default 7777>')
         sys.exit()
      elif opt in ("-a", "--address"):
         address = arg
      elif opt in ("-p", "--port"):
         port = arg
    logger.info('Send Client started with parameters -p %s -a %s', port, address)
    # Make and bind socket
    s = socket(AF_INET, SOCK_STREAM) # Создать сокет TCP
    try:
      s.connect((address, port)) # Соединиться с сервером
    except:
      logger.error('Could not connect to server %s:%s', address, port)
      return
    username = input('Your name: ')
    while True:  
        msg = input('Your message: ')
        if msg == 'exit':
            s.close()
            break
        send_message(s, username, msg)


if __name__ == "__main__":
   main(sys.argv[1:])
