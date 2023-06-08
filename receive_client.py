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


@log(logger)
def receive_message(mysocket):
    data = mysocket.recv(1000000)
    resp_msg_dict = json.loads(data.decode('utf-8'))
    print(f'{datetime.fromtimestamp(float(resp_msg_dict["time"]))} {resp_msg_dict["from"]}: {resp_msg_dict["message"]}')


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
    logger.info('Receive Client started with parameters -p %s -a %s', port, address)
    # Make and bind socket
    s = socket(AF_INET, SOCK_STREAM) # Создать сокет TCP
    try:
      s.connect((address, port)) # Соединиться с сервером
    except:
      logger.error('Could not connect to server %s:%s', address, port)
      return
    while True:  
        receive_message(s)


if __name__ == "__main__":
   main(sys.argv[1:])
