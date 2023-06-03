from socket import *
import time
from datetime import datetime
import sys, getopt  # to work with command line arguments
import json
import threading


presense_message = {
    "action": "presence",
    "time": time.mktime(datetime.now().timetuple()),
    "type": "status",
    "user": {
        "account_name": "GigaChad",
        "status": "I'm still alive!"
    }
}


def send_presence(mysocket):
    msg = json.dumps(presense_message)
    mysocket.send(msg.encode('utf-8'))
    data = mysocket.recv(1000000)
    resp_msg_dict = json.loads(data.decode('utf-8'))
    print('Server responded to presence message with code: ', resp_msg_dict["response"])

def main(argv):
    # Parse command line arguments for port and address
    address = 'localhost'
    port = 7777
    opts, args = getopt.getopt(argv,"ha:p:",["address=","port="])
    for opt, arg in opts:
      if opt == '-h':
         print ('server.py -a <accepted client address. default - all> -p <listen port. default 7777>')
         sys.exit()
      elif opt in ("-a", "--address"):
         address = arg
      elif opt in ("-p", "--port"):
         port = arg
    # Make and bind socket
    s = socket(AF_INET, SOCK_STREAM) # Создать сокет TCP
    s.connect((address, port)) # Соединиться с сервером
    msg_sent_flag = False
    while True:  
       if ((datetime.now().second % 5) == 0):         
          if not msg_sent_flag:           
            send_presence(s)
            msg_sent_flag = True
       else:
          msg_sent_flag = False
    s.close()



if __name__ == "__main__":
   main(sys.argv[1:])

