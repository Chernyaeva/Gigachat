# Программа сервера для получения приветствия от клиента и отправки ответа
from socket import *
import time
from datetime import datetime
import sys, getopt  # to work with command line arguments
import json
import logging
import Logs.config_server_log
from decorators import log
from select import select

#initialyze logger
logger = logging.getLogger('server')


@log(logger)
def read_requests(r_clients, all_clients):
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


@log(logger)
def write_responses(requests, w_clients, all_clients):
    """ Just resend received messages to all clients, except ones that are sending
    """
    for client in w_clients:
            for r_client in requests:
                req_data = requests[r_client].encode('utf-8')
                # Check type of request (message or not)
                try:
                    req_type = json.loads(req_data)['action']
                except:
                    logger.error('Could not parse message from Client {} {} disconnected'.format(client.fileno(),client.getpeername()))
                else:                       
                    if req_type == "msg":
                        print(f'sending message {req_data} to client {client}') 
                        try:
                            # Prepare and send data to clients                   
                            client.send(req_data)
                        except: # Client disconnected in meantime
                            logger.info('Client {} {} disconnected'.format(client.fileno(),client.getpeername()))
                            client.close()
                            all_clients.remove(client)


@log(logger)
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
    logger.info('Server started with parameters -p %s -a %s', port, address)
    # Make and bind socket
    clients = []
    s = socket(AF_INET, SOCK_STREAM) # Make TCP socket
    try:
        s.bind((address, port)) # Bind socket to port
    except:
        logger.error('Could not bind socket')
        return    
    s.listen(5) # Activate listening mode for socket. Accept not more than 5 clients simulteneously.
    s.settimeout(0.2) 
    
    while True:
        try:
            client, addr = s.accept()
        except OSError as e:
            pass # timeout
        else:
            logger.info("Client %s tries to connect",str(addr))
            clients.append(client)
        finally:
            # check for read/write events
            wait = 10
            r = []
            w = []
            try:
                r, w, e = select(clients, clients, [], wait)
            except:
                pass
            requests = read_requests(r, clients) # Save client request in dict
            if requests:
                write_responses(requests, w, clients) # Send responses to clients


if __name__ == "__main__":
   main(sys.argv[1:])