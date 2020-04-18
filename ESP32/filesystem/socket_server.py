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
        self.cmd = ''
        self.loop = ''
        self.connect = False
        self.upload = False
        self.file = ''
        self.greeting = 'Hi.'
        self.funcs = {
            'stop' : self.exit_server(),
            'quit' : self.exit_server(),
            'connect': self.perm_connect(),
            'upload': self.handle_upload(),
        }
        run(self.mainrun(self.host, self.port))

    async def perm_connect(self):
        self.connect = True
        self.port =  int.from_bytes(rand(2), 'little')
        await self.writer.awrite(str(self.port))
        await self.writer.drain()
        print(1)
        self.server_task.cancel()
        print(2)
        self.l.run_until_complete(self.server.close())
        print(3)
        self.reader.close()
        print(4)
        self.writer.close()
        print(5)
        print('closed server and streams')
        self.server = await start_server(self.callback, self.host, self.port)
        print('Created server on port {}'.format(self.port))
        await self.l.create_task(self.server)

    async def handle_upload(self):
        print('in upload')
        self.upload = True
        await self.writer.awrite('Filename?\n')

    async def assign_streams(self, reader, writer):
        self.reader = reader
        self.writer = writer

    async def handle_input(self, data):
        self.cmd = data.decode('utf-8').strip('\n')
        if self.upload:
            if self.cmd == 'done':
                print('Done upload')
                self.upload = False
                self.file.close()
                self.file = ''
            elif self.file == '':
                filename = self.cmd
                print('Filename: {}'.format(filename))
                if not (filename == 'boot.py' or filename == 'main.py'):
                    print('Opened {}'.format(filename))
                    self.file = open(filename,'w+')
                    await self.writer.awrite('Ok. Begin upload\n')
            else:
                print('Wrote data'.format(data))
                self.file.write(a2b_base64(data).decode('utf-8'))
        elif self.cmd in self.funcs:
            await self.funcs[self.cmd]
        else:
            await self.writer.awrite('server echo: ' + self.cmd + '\n')
            await self.writer.drain()

    async def callback(self, reader, writer):
        self.reader = reader
        self.writer = writer
        if self.connect:
            self.greeting = self.greeting + ' >.<;'
        await self.writer.awrite(self.greeting + '\n')
        await self.writer.drain()
        while True:
            print('Waiting for data')
            data = await self.reader.read(1024)
            print('server recieved: {}'.format(data))
            print('size of data: {}'.format(len(data)))
            await self.handle_input(data)

    def handle_errors(self, loop, context):
        print(context['message'])
        print('{}: {}'.format(type(context['exception']), context['exception']))

    async def exit_server(self):
        print('closing writer stream')
        await self.writer.awrite(':(\n')
        await self.writer.drain()
        await self.writer.aclose()
        self.server.close()
        self.l.stop()

    async def busywork(self):
        while True:
            print('Doing busywork')
            await sleep_ms(10000)

    async def mainrun(self, host, port):
        self.l = get_event_loop()
        self.l.set_exception_handler(self.handle_errors)
        print('Opening server on port {}'.format(port))
        self.server = start_server(self.callback, host, port)
        self.server2 = start_server(self.callback, host, 1000)
        self.server_task = self.l.create_task(self.server)
        self.server2_task = self.l.create_task(self.server2)
        self.l.create_task(self.busywork())
        self.l.run_forever()
