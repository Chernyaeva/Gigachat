# Server programm
import socket
import time
from datetime import datetime
import sys, getopt  # to work with command line arguments
import json
import logging
import Logs.config_server_log
import threading
from decorators import log
from select import select
from metaclasses import ServerVerifier
from server_db import ServerStorage
from PyQt5 import  QtWidgets, uic
from decorators import login_required


#initialyze logger
logger = logging.getLogger('server')


# Дескриптор для описания порта:
class Port:
    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            logger.critical(f'Port number {value} is not allowed. Allowed values from 1024 to 65535.')
            exit(1)
        # Если порт прошел проверку, добавляем его в список атрибутов экземпляра
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class Server(threading.Thread, metaclass=ServerVerifier):
    port = Port()

    def __init__(self, listen_address, listen_port, database):
        # Параментры подключения
        self.addr = listen_address
        self.port = listen_port
        # Список подключённых клиентов.
        self.clients = []
        # Словарь содержащий сопоставленные имена и соответствующие им сокеты.
        self.present_users = {}
        #Server database
        self.storage = database
        super().__init__()

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

    @login_required
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
                logger.error('Could not parse message {} from Client {} {}'.format(req_data,r_client.fileno(),r_client.getpeername()))
            else:                       
                if req_type == "msg":
                    if request['to'] in self.present_users.keys():
                        print(f'sending message {request["message"]} to client {request["to"]}') 
                        try:
                            # Prepare and send data to client
                            client = self.present_users[request['to']]                   
                            client.send(req_data)
                            self.storage.save_message(request["from"], request["to"], request["message"])
                        except: # Client disconnected in meantime
                            logger.info('Client {} {} disconnected'.format(client.fileno(),client.getpeername()))
                            client.close()
                            all_clients.remove(client)
                elif req_type == "presence":
                    self.present_users[request['user']['account_name']] = r_client
                    auth_result = self.storage.user_login(request['user']['account_name'], request['user']['password_hash'])
                    if auth_result == -1:
                        client = self.present_users[request['user']['account_name']]
                        client.close()
                        all_clients.remove(client) 
                elif req_type == "add_contact":
                    self.storage.add_contact(request['user_login'], request['user_id'])
                elif req_type == "get_contacts":
                    contacts = self.storage.get_contacts(request['user_login'])
                    if len(contacts) and request['user_login'] in self.present_users.keys():
                        print(f'sending contacts {contacts} to client {request["user_login"]}') 
                        try:
                            # Prepare and send data to client
                            client = self.present_users[request["user_login"]]                   
                            client.send(json.dumps(contacts))
                        except: # Client disconnected in meantime
                            logger.info('Client {} {} disconnected'.format(client.fileno(),client.getpeername()))
                            client.close()
                            all_clients.remove(client)       


    def make_response(self, rcv_dict):
        snd_msg = {}
        if rcv_dict['action'] == 'presence':
            snd_msg['response'] = 202 # Accepted
        else:
            snd_msg['response'] = 500 # Server error 
            snd_msg["alert"] = "server could not find good response"  
        snd_msg['time'] = time.mktime(datetime.now().timetuple())
        return json.dumps(snd_msg).encode('utf-8')    


    def run(self):
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
                wait = 1
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
    # Initalize database
    database = ServerStorage()
    # Make and bind socket
    server = Server(address, port,database)
    server.daemon = True
    server.start()

    app = QtWidgets.QApplication(sys.argv)
    window = uic.loadUi('ServerMain.ui')
    #window.btnQuit.clicked.connect(app.quit)
    window.show()
    users = database.get_users()
    window.ClientsList.addItems(users)
    users_hystory =  database.get_users_history()
    window.ClientsStatsList.addItems(users_hystory)
    window.ParametersList.addItems([
        f'Server listen address is {address}',
        f'Server port is {port}'
    ])
    sys.exit(app.exec_())

    

if __name__ == "__main__":
   main(sys.argv[1:])