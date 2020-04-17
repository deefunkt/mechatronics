from asyncio import get_event_loop, open_connection, start_server, run, sleep

class SocketClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connection = ''
        self.reader = ''
        self.writer = ''
        run(self.init_loop())

    async def init_loop(self):
        self.l = get_event_loop()
        self.l.create_task(self.open_comms())
        self.l.create_task(self.send_file())
        self.l.run_forever()
        
    async def send_file(self):
        while True:
            tosend = input()
            print(tosend)
            await self.writer.awrite(tosend)
            await self.writer.drain()

    async def open_comms(self):
        await sleep(2)  # Allow server to get up
        print('Opening connection to {}:{}'.format(self.host, self.port))
        self.reader, self.writer = await open_connection(self.host, self.port)
        while True:
            recdata = await self.reader.readline()
            print(recdata)

client = SocketClient('10.0.0.32', '8888')

