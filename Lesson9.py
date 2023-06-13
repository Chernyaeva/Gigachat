from subprocess import Popen, PIPE
import ipaddress
from tabulate import tabulate

def ping_ip(ip_address):
    args = ['ping', ip_address, '-c 1', '-w 1']
    reply = Popen(args, stdout=PIPE, stderr=PIPE)
    CODE = reply.wait()
    if CODE == 0:
        return True
    else:
        return False

def host_ping(ip_address_list):
    for ip_address in ip_address_list:
        if ping_ip(str(ip_address)):
            print(f'{ip_address} available')
        else:
            print(f'{ip_address} is not available')

def host_range_ping(start_address, end_address):
    ip_address = start_address
    while ip_address <= end_address:
        if ping_ip(str(ip_address)):
            print(f'{ip_address} available')
        else:
            print(f'{ip_address} is not available')
        ip_address += 1

def host_range_ping_tab(start_address, end_address):
    result_list = []
    ip_address = start_address
    while ip_address <= end_address:
        if ping_ip(str(ip_address)):
            result_list.append({'Reachable': ip_address})
        else:
            result_list.append({'UnReachable': ip_address})
        ip_address += 1
    print(tabulate(result_list, headers='keys', tablefmt="pipe"))

#ip_address_list = ipaddress.ip_network('8.8.8.0/28')
#host_ping(ip_address_list)

start_ip = ipaddress.ip_address('8.8.8.8')
end_ip = ipaddress.ip_address('8.8.8.11')
host_range_ping_tab(start_ip, end_ip)