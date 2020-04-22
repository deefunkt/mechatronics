'''
FIXME: 2 async functions not the best idea, open comms, then sendfile.
TODO: is it easier to just use raw python sockets? maybe desktop doesnt need async
'''

import argparse
import socket
from time import sleep
from transpile import convert

'''
Opens a connection to ESP32 board and sends a file over.'''

def send(src_file, dest_file, data, HOST = '10.0.0.32', PORT = 8888):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(f'Opening connection to {HOST}:{PORT}')
        s.connect((HOST, PORT))
        sleep(1)
        connection = ''
        s.sendall(b'Hello ESP.')
        while True:
            data = s.recv(1024).decode('utf-8')
            if 'Hi.' in data:
                if connection == '':
                    s.sendall(b'connect')
                    connection = 'requested'
                elif connection == 'made':
                    s.sendall(b'upload')
                print('Recieved greeting')
            elif 'simon says' in data.lower():
                pass
            elif connection == 'requested':
                newport = int(data)
                print(f'port recieved {newport}')
                s.close()
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((HOST, newport))
                sleep(1)
                connection = 'made'
            elif connection == 'made':
                if 'Filename?' in data:
                    s.sendall(src_file.encode())
                    sleep(1)
                    s.sendall(data)
                    sleep(3)
                    s.sendall(b'done')
                    s.sendall(b'stop')
            elif ':(' in data:
                s.close()
                break
            print('Received', repr(data))
    print('Exiting socket client')
        # send
        # recieve
        # parse results