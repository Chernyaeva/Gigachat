# Программа сервера для получения приветствия от клиента и отправки ответа
import socket
import time
from datetime import datetime
import sys, getopt  # to work with command line arguments
import json
import logging
import Logs.config_server_log
from decorators import log
from select import select
from metaclasses import ServerVerifier

#initialyze logger
logger = logging.getLogger('server')


# Дескриптор для описания порта:
class Port:
    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            logger.critical(f'Port number {value} is not allower. Allowed values from 1024 to 65535.')
            exit(1)
        # Если порт прошел проверку, добавляем его в список атрибутов экземпляра
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class Server(metaclass=ServerVerifier):
    port = Port()

    def __init__(self, listen_address, listen_port):
        # Параментры подключения
        self.addr = listen_address
        self.port = listen_port

        # Список подключённых клиентов.
        self.clients = []

        # Словарь содержащий сопоставленные имена и соответствующие им сокеты.
        self.present_users = {}

    def bind_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Make TCP socket
        try:
            s.bind((self.addr, self.port)) # Bind socket to port
        except:
            logger.error('Could not bind socket')
            exit(1)
        s.settimeout(0.2) 
        self.sock = s   
        self.sock.listen(5) # Activate listening mode for socket. Accept not more than 5 clients simulteneously.
        
    def read_requests(self, r_clients, all_clients):
        """ Read requests from list of clients
        """
        requests = {} # Dict of requests from clients {socket: request}
        for client in r_clients:
            try:
                data = client.recv(1024).decode('utf-8')
                requests[client] = data
            except:
                logger.info('Client {} {} disconnected'.format(client.fileno(), client.getpeername()))
                all_clients.remove(client)
        return requests


    def write_responses(self, requests, w_clients, all_clients):
        """ Just resend received messages to all clients, except ones that are sending
        """
        for r_client in requests:
            req_data = requests[r_client].encode('utf-8')
            # Check type of request (message or not)
            try:
                request = json.loads(req_data)
                req_type = request['action']
            except:
                logger.error('Could not parse message from Client {} {}'.format(r_client.fileno(),r_client.getpeername()))
            else:                       
                if req_type == "msg":
                    if request['to'] in self.present_users.keys():
                        print(f'sending message {request["message"]} to client {request["to"]}') 
                        try:
                            # Prepare and send data to client
                            client = self.present_users[request['to']]                   
                            client.send(req_data)
                        except: # Client disconnected in meantime
                            logger.info('Client {} {} disconnected'.format(client.fileno(),client.getpeername()))
                            client.close()
                            all_clients.remove(client)
                elif req_type == "presence":
                    self.present_users[request['user']['account_name']] = r_client


    def make_response(self, rcv_dict):
        snd_msg = {}
        if rcv_dict['action'] == 'presence':
            snd_msg['response'] = 202 # Accepted
        else:
            snd_msg['response'] = 500 # Server error 
            snd_msg["alert"] = "server could not find good response"  
        snd_msg['time'] = time.mktime(datetime.now().timetuple())
        return json.dumps(snd_msg).encode('utf-8')    


    def main_loop(self):
        self.bind_socket()
        while True:
            try:
                client, addr = self.sock.accept()
            except OSError as e:
                pass # timeout
            else:
                logger.info("Client %s tries to connect",str(addr))
                self.clients.append(client)
            finally:
                # check for read/write events
                wait = 10
                r = []
                w = []
                try:
                    r, w, e = select(self.clients, self.clients, [], wait)
                except:
                    pass
                requests = self.read_requests(r, self.clients) # Save client request in dict
                if requests:
                    self.write_responses(requests, w, self.clients) # Send responses to clients


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
    logger.info('Server started with parameters -p %s -a %s', port, address)
    # Make and bind socket
    server = Server(address, port)
    server.main_loop()


if __name__ == "__main__":
   main(sys.argv[1:])