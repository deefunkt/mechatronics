'''
TODO: implement decoding of hex/base64 encoded files
FIXME: fix graceful server shutdown
TODO: implement dynamic server creation rather than 2 in the beginning
'''

from uasyncio import get_event_loop, open_connection, start_server, run, sleep_ms
from uos import urandom as rand
from ubinascii import a2b_base64


class SocketServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.loop = ''
        self.conncount = 0
        self.funcs = {
            'stop' : self.exit_server,
            'quit' : self.quit,
            'connect': self.perm_connect,
            'upload': self.handle_upload,
        }
        print('Opening server on port {}'.format(port))
        self.server = start_server(self.callback, host, port)
        print('Funcs avail: {}'.format(dir(self.server)))
        self.servers = [self.server]
        self.connections = {}
        run(self.server)
        run(self.mainrun(self.host, self.port))

    async def perm_connect(self, peer):
        self.connections[peer]['connect'] = True
        print('Perm connection request recieved from {}'.format(peer))
        new_port =  int.from_bytes(rand(2), 'little')
        await self.connections[peer]['writer'].awrite(str(new_port) + '\n')
        await self.connections[peer]['writer'].drain()
        await self.exit_server(peer)
        # print('Exiting task')        
        # await self.server_task.cancel()
        # print('Done')
        # print('Closed server and streams')
        self.servers.append(start_server(self.callback, self.host, new_port))
        print('Created server on port {}'.format(new_port))
        run(self.servers[-1])

    async def handle_upload(self, peer):
        print('in upload')
        self.connections[peer]['upload'] = True
        await self.connections[peer]['writer'].awrite('Filename?\n')

    async def handle_input(self, data, peer):
        cmd = data.decode('utf-8').strip('\n')
        if  self.connections[peer]['upload']:
            if cmd == 'done':
                print('Done upload.')
                self.connections[peer]['upload'] = False
                self.connections[peer]['upload_file'].close()
                self.connections[peer]['upload_file'] = ''
            elif self.connections[peer]['upload_file'] == '':
                filename = cmd
                print('Filename: {}'.format(filename))
                if not (filename == 'boot.py' or filename == 'main.py'):
                    print('Opened {}'.format(filename))
                    self.connections[peer]['upload_file'] = open(filename,'w+')
                    await self.connections[peer]['writer'].awrite('Ok. Begin upload.\n')
            else:
                print('Wrote data.')
                self.connections[peer]['upload_file'].write(a2b_base64(data).decode('utf-8'))
        elif cmd in self.funcs:
            await self.funcs[cmd](peer)
        elif cmd.lower().startswith('simon says'):
            await self.connections[peer]['writer'].awrite('Simon didn\'t say that.\n')
            await self.connections[peer]['writer'].drain()
        else:
            await self.connections[peer]['writer'].awrite('Simon says ' + cmd + '\n')
            await self.connections[peer]['writer'].drain()

    async def callback(self, reader, writer):
        peer = reader.get_extra_info('peername')
        self.conncount += 1
        print('Num connections: {}'.format(self.conncount))
        self.connections[str(peer)] = {
            'reader': reader,
            'writer': writer,
            'upload': False,
            'perm_connected': False,
            'upload_file': '',
            'greeting': 'Hi.',
            'conn_no' : self.conncount,
            'exit' : False
            }
        peer = str(peer)
        print('Connection from {}'.format(peer))
        if self.connections[peer]['perm_connected']:
            self.connections[peer]['greeting'] = 'Hi. >.<;'
        await writer.awrite(self.connections[peer]['greeting'] + '\n')
        await writer.drain()
        while True:
            if self.connections[peer]['exit']:
                break
            print('Waiting for data')
            data = await reader.read(1024)
            print('server recieved: {}'.format(data))
            await self.handle_input(data, peer)
        print('Closing reader writer streams')
        reader.close()
        writer.close()

    def handle_errors(self, loop, context):
        print(context['message'])
        print('{}: {}'.format(type(context['exception']), context['exception']))

    async def exit_server(self, peer):
        print('Exiting server, streams for {}'.format(peer))
        self.connections[peer]['exit'] = True
        self.connections[peer]['writer'].close()
        self.connections[peer]['reader'].close()
        await sleep_ms(20)
        print(len(self.servers))
        self.servers[self.connections[peer]['conn_no'] - 1].close()
        self.conncount -= 1
        print('Num connections: {}'.format(self.conncount))
        print('Closed')
 
    def quit(self):
        for peer in self.connections:
            await self.connections[peer]['writer'].awrite(':(\n')
            await self.connections[peer]['writer'].drain()
            await self.exit_server(peer)
        self.l.stop()
        self.l.close()

    async def busywork(self, text):
        while True:
            print('Doing busywork' + text)
            await sleep_ms(10000)
    
    async def pulse_led(self):
        from machine import Pin, PWM
        pwm2 = PWM(Pin(4), freq=5000, duty=1)
        # a = [i for i in range(-10, 11)]
        # seq = [math.ceil(5/math.cosh(i/3)) for i in a]
        seq = [1, 1, 1, 1, 2, 2, 3, 4, 5, 5, 5, 5, 5, 4, 3, 2, 2, 1, 1, 1, 1]
        while True:
            for i in seq:
                pwm2.duty(i)
                await sleep_ms(50)


    async def mainrun(self, host, port):
        self.l = get_event_loop()
        # self.l.set_exception_handler(self.handle_errors)
        self.l.create_task(self.busywork(' abc'))
        self.l.create_task(self.pulse_led())
        self.l.run_forever()


