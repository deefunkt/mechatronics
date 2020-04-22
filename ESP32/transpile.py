'''
TODO: change print messages to be configurable with verbosity and direct sending
'''

import argparse
from binascii import b2a_base64, a2b_base64

def initialize():
    parser = argparse.ArgumentParser(description='''
Reads a file, and outputs the repl commands to write the contents again to disk.
Useful to copy executable code to micropython systems using the paste mode once.
Write code, run this program on the file, paste the output on the micropython serial interface.''',
                                    formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('src_file', type=str, help='File containing contents to be transferred')
    parser.add_argument('-d','--dest', dest='dest_file', metavar='FILE',
                        help='Filename of destination file on the micropython system, default is src_file name')
    parser.add_argument('--send', action='store_true', help='Transfer directly to ESP32 server, default false')
    parser.add_argument('--dest_ip', help='Destination IP of the board', default='10.0.0.32')
    parser.add_argument('-p', metavar='PORT', dest='dest_port', help='Destination port of the board', default='8888')
    args = parser.parse_args()
    init_vars = {
        'src_file': args.src_file,
        'dest_file': args.dest_file,
        'send': args.send,
        'dest_ip': args.dest_ip,
        'dest_port':args.dest_port
    }
    return init_vars
    
def convert(src_file):
    with open(src_file) as f:
        fileread = f.read()
    return b2a_base64(fileread.encode('utf-8'))


'''
Opens a connection to ESP32 board and sends a file over.'''

def send(dest_file, filedata, HOST = '10.0.0.32', PORT = 8888):
    import socket
    from time import sleep
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
                    s.sendall(dest_file.encode())
                    sleep(1)
                    s.sendall(filedata)
                    sleep(3)
                    s.sendall(b'done')
                    s.sendall(b'stop')
            elif ':(' in data:
                s.shutdown(socket.SHUT_RDWR)
                s.close()
                print(f'Socket handles: {s.fileno()}')
                break
            print('Received', repr(data))
    print('Exiting socket client')

if __name__ == "__main__":
    init = initialize()
    if init['dest_file'] == None:
        init['dest_file'] = init['src_file']
    print(f"Source filename: {init['src_file']}")
    print(f"Destination filename: {init['dest_file']}")
    if init['send']:
        send(dest_file = init['dest_file'], 
            filedata = convert(init['src_file']))
    else:
        print('Copy and paste from below:\n\n')
        print(f"with open('{init['dest_file']}', 'w+') as f:")
        print('    f.write(a2b_base64(' + str(convert(init['src_file'])) + ').decode(\'utf-8\'))')

    
