#!/bin/python3
import os
import socket
import ipaddress
import time
import logging
import sys
import argparse
import threading



def handle_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip_address',"--ip",help='will use 127.0.0.1 if none provided', default=ipaddress.ip_address("127.0.0.1"))
    parser.add_argument("-p",'--port_address', help = 'will use a random unprivileged port if none provided', default=0, type=int)
    parser.add_argument("-l",'--listen_mode', action="store_true",default=False,)
    parser.add_argument('--log_level', default=20, type=int)
    parser.add_argument('--log_file', default="", type=str)
    
    config = parser.parse_args()
    config.recvlength = 2048
    config.bye_str = "bye"
    config.exit_command = "exit"
    config.str_delim = " , "
    config.retry_wait_time=2
    return config




class host_info :
    ip : ipaddress.ip_address
    port : int
    
    def __init__ (self,ip = None, port = None):
        self.ip = ip
        self.port = port
    def __str__(self)->str:
        return str(self.ip) + config.str_delim + str(self.port)

def handle_tcp_client(client_socket):
    while True:
        data, wtf = client_socket.recvfrom(config.recvlength)

        #probably a ^C from the other side
        if ( len ( data ) == 0 ):
            break
        data = data.decode()[0:len(data)-1]
        
        
        print(data)

        
        if(data == config.exit_command):
            break
    client_socket.send(config.bye_str.encode())
    logger.info(f"connection closed {client_socket}")
    client_socket.close()



def bind_and_retry(sock, ip : str, port : int = 0)->socket.socket:
    while True:
        try :
            sock.bind((ip, port))
            break
        except Exception as e :
            logger.error(f"error binding {e}")
            logger.debug(f"retrying after {config.retry_wait_time} secods")
        time.sleep(config.retry_wait_time)
    return sock

def listen_mode_udp(sock : socket.socket):
    return
def listen_mode_tcp(sock : socket.socket):
    """
    gets a binded tcp socket and starts listening for connections and accept them
    """
    while True:
            sock.listen(1)

            connection_socket, client = sock.accept()

            logger.info(f"connected from {client}")
            handle_tcp_client(connection_socket)

    return

#need testing
def client_mode_tcp(sock : socket.socket)->int:

    error_code : int = 0
    server = host_info(config.ip_address, config.port_address)

    try:
        sock.connect((str(server.ip), server.port))
        logger.info(f"connected to {server}")
    except Exception as e:
        logger.error(f"couldn't connect to {server} error : {e}")
        error_code = 1
        return error_code

    try:
        while True:
            data  = input()
            data += '\n'
            sock.send(data.encode())

    except KeyboardInterrupt:
        logger.info(f"got ^C disconnecting from {server}")
        sock.close()
            
    return error_code

def verify_config():
    if config.listen_mode == False and config.port_address == 0:
        logger.error("need to provide a port when connecting")
        exit(1)

if __name__ == "__main__":
    #default config

    logger = logging.getLogger()
    config = handle_args()
    logging.basicConfig(filename=config.log_file, level=config.log_level)

    logger.debug(config)
    verify_config()


    
    sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    
    if( config.listen_mode == True ):

        sock = bind_and_retry(sock, config.ip_address.__str__(),config.port_address)
        logger.debug(sock)

        listen_mode_tcp(sock)

    if ( config.listen_mode == False ):
        logger.debug(sock)
        
        client_mode_tcp(sock)

    sock.close()


