'''
FIXME: fix graceful server shutdown. Sockets arent closing, server only has  'close', 'send', 'throw', 'pend_throw' as functions. 
    Cant find documentation in asyncio for these, is it an old version?
    installed version checked to be v3 using print(uasyncio.__version__)
FIXME: permanent connection not working as expected. an IP can either visit the same port because of improper socket shutdown, or 
the server gets it wrong that the previous port has been the one who sent the message. perhaps the protocol needs to implement a 'where did you come from'
question to the client. Alternatively uploads can be protected by an encrypted challenge.
TODO: implement a 'ready to recieve next chunk' functionality for big files incoming
'''

from uasyncio import get_event_loop, open_connection, start_server, run, sleep_ms
from uos import urandom as rand
from ubinascii import a2b_base64
from machine import Pin, PWM, TouchPad, reset


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
            'reset' : self.reset
        }
        print('Opening server on port {}'.format(port))
        self.connections = {}
        self.duty_led = 800
        run(self.mainrun(self.host, self.port))

    async def server_creator(self, host, port):
        self.server = await start_server(self.callback, host, port)
        print('Funcs avail: {}'.format(dir(self.server)))
        
    async def reset(self, peer):
        if self.connections[peer]['perm_connected']:
            await self.connections[peer]['writer'].awrite('Initiating reset' + '\n')
            await self.connections[peer]['writer'].drain()
            await self.exit_server(peer)
            reset()

    async def perm_connect(self, peer):
        self.connections[peer]['perm_connected'] = True
        print('Perm connection request recieved from {}'.format(peer))
        new_port =  int.from_bytes(rand(2), 'little')
        await self.connections[peer]['writer'].awrite(str(new_port) + '\n')
        await self.connections[peer]['writer'].drain()
        await self.exit_server(peer)
        self.l.create_task(self.server_creator(self.host, new_port))
        print('Created server on port {}'.format(new_port))

    async def handle_upload(self, peer):
        # if self.connections[peer]['perm_connected']:
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
        elif cmd.lower().startswith('update_led'):
            self.duty_led = int(cmd.split(' ')[1].strip('\n'))
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
            'exit' : False,
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
        await self.connections[peer]['writer'].awrite(':(\n')
        await self.connections[peer]['writer'].drain()
        self.connections[peer]['writer'].close()
        self.connections[peer]['reader'].close()
        await sleep_ms(20)
        self.server.close()
        self.conncount -= 1
        print('Num connections: {}'.format(self.conncount))
        print('Closed')
 
    def quit(self, peer):
        for peer in self.connections:
            await self.exit_server(peer)
        self.l.stop()
        self.l.close()

    async def get_time(self):
        print('Importing urequests')
        import urequests as r
        while True:
            try:
                resp = r.get('https://worldtimeapi.org/api/ip')
                print('Current time: {}'.format(resp.json()['datetime'][0:16]))
            except Exception as e:
                print(repr(e))
            finally:
                await sleep_ms(1800000)
    
    async def pulse_led(self):
        pwm2 = PWM(Pin(4), freq=5000, duty=1)
        # a = [i for i in range(-10, 11)]
        # seq = [math.ceil(5/math.cosh(i/3)) for i in a]
        seq = [1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 2, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1]
        while True:
            for i in seq:
                pwm2.duty(i)
                await sleep_ms(50)

    async def pulse_lightbar(self):
        pwm2 = PWM(Pin(2), freq=1000, duty=1)
        t = TouchPad(Pin(14))
        # a = [i for i in range(-50, 51)]
        # seq = [math.ceil(1023/math.cosh(i/20)) for i in a]
        # seq= [710, 719, 728, 738, 747, 756, 765, 775, 784, 793, 802, 811, 
        # 820, 829, 838, 846, 855, 863, 872, 880, 888, 896, 904, 912, 919, 
        # 926, 933, 940, 947, 953, 959, 965, 971, 977, 982, 987, 991, 996, 
        # 1000, 1003, 1007, 1010, 1013, 1015, 1017, 1019, 1021, 1022, 1023, 
        # 1023, 1023, 1023, 1023, 1022, 1021, 1019, 1017, 1015, 1013, 1010, 
        # 1007, 1003, 1000, 996, 991, 987, 982, 977, 971, 965, 959, 953, 947, 
        # 940, 933, 926, 919, 912, 904, 896, 888, 880, 872, 863, 855, 846, 838, 
        # 829, 820, 811, 802, 793, 784, 775, 765, 756, 747, 738, 728, 719, 710]
        # seq = [math.ceil(1024/math.cosh(i/20)) for i in a]
        seq = range(1000,1124)
        while True:
            # Returns a smaller number when touched
            pwm2.duty(self.duty_led)
            await sleep_ms(50)
                

    async def mainrun(self, host, port):
        self.l = get_event_loop()
        # self.l.set_exception_handler(self.handle_errors)
        self.l.create_task(self.server_creator(host, port))
        self.l.create_task(self.get_time())
        self.l.create_task(self.pulse_led())
        self.l.create_task(self.pulse_lightbar())
        self.l.run_forever()


