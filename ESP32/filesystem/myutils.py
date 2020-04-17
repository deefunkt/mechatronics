'''
TODO: extend cmp_file to be more 'diff' like - line by line comparator. mostly formatting output.
'''

import network

class Logger:
    def __init__(self, level='verbose'):
        self.level = level
    
    def debug(self, msg):
        print('DEBUG: {}'.format(msg))
    
    def info(self, msg):
        print('INFO: {}'.format(msg))

def wifi_connect(ssid='', password=''):
    if ssid=='' or password=='':
        with open('wificreds.txt') as f:
            creds = f.readlines()
        ssid = creds[0].split('ssid: ')[1].strip('\\n')
        password = creds[1].split('password: ')[1].strip('\\n')
    wlan = network.WLAN(network.STA_IF) # create station interface
    wlan.active(True)
    wlan.config(dhcp_hostname='esp32CAM')
    if not wlan.isconnected():
        print('MYUTIL: Connecting to network {}...'.format(ssid))
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('MYUTIL: Hostname: {}'.format(wlan.config('dhcp_hostname')))
    print('MYUTIL: Network config:\\n(IP address, subnet mask, gateway and DNS server)\\n{}'.format(wlan.ifconfig()))

def wifi_ap(ssid='ESP'):
    print('MYUTIL: Creating WIFI AP')
    ap = network.WLAN(network.AP_IF) # create access-point interface
    ap.active(True)         # activate the interface
    ap.config(essid='ESP-AP') # set the ESSID of the access point
    print('MYUTIL: AP created: {}'.format(ssid))

def cat(file):
    with open(file) as f:
        print(f.read())

def cmp_file(file1, file2):
    f1 = open(file1)
    f2 = open(file2)
    from uhashlib import sha1
    return (sha1(f1.read()).digest() == sha1(f2.read()).digest())