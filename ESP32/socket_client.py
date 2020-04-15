from asyncio import get_event_loop, open_connection, start_server, sleep_ms, run

async def echo_client(line, result, sockaddr):
    await sleep_ms(1000)  # Allow server to get up
    print('Opening connection to {}:{}'.format(*sockaddr))
    reader, writer = await open_connection(*sockaddr)
    print('client Sending: {}'.format(line))
    await writer.awrite(line)
    data = await reader.readline()
    await writer.aclose()
    print('server Response Result: \\n{}'.format(data))

