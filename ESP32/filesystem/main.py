from myutils import *
from machine import reset
from socket_server import SocketServer
from ubinascii import a2b_base64

l = Logger()
l.info('Started main.py')
wifi_connect()
wifi = network.WLAN(network.STA_IF)
ap = network.WLAN(network.AP_IF)
ss = SocketServer('10.0.0.32', 8888)



