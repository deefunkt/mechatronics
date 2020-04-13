from myutils import *
import machine

l = Logger()
l.info('Started main.py')
wifi_connect()
wifi = network.WLAN(network.STA_IF)
ap = network.WLAN(network.AP_IF)

