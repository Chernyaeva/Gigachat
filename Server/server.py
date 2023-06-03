# Программа сервера для получения приветствия от клиента и отправки ответа
from socket import *
import time
from datetime import datetime
import sys, getopt  # to work with command line arguments
import json


def make_response(rcv_dict):
    snd_msg = {}
    if rcv_dict['action'] == 'presence':
        snd_msg['response'] = 202 # Accepted
    else:
        snd_msg['response'] = 500 # Server error 
        snd_msg["alert"] = "server could not find good response"  
    snd_msg['time'] = time.mktime(datetime.now().timetuple())
    return json.dumps(snd_msg).encode('utf-8')    


def main(argv):
    # Parse command line arguments for port and address
    address = ''
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
    s = socket(AF_INET, SOCK_STREAM) # Make TCP socket
    s.bind((address, port)) # Bind socket to port 
    s.listen(5) # Activate listening mode for socket. Accept not more than 5 clients simulteneously.
    client, addr = s.accept()
    while True:       
        data = client.recv(1000000)
        rcv_dict = json.loads(data.decode('UTF-8'))
        print('Сообщение: ', data.decode('utf-8'), ', было отправлено клиентом: ', addr)
        client.send(make_response(rcv_dict))
        # client.close()



if __name__ == "__main__":
   main(sys.argv[1:])