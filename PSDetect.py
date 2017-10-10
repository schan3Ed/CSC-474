import time
from scapy.all import *
import signal
import sys

def signal_handler(signal, frame):
    print ""
    sys.exit(0)

ti = []
po = []
IP = []

signal.signal(signal.SIGINT, signal_handler)

def call_back(packet):
    try:
        ip = packet.src
        port = packet.dport
        if ip not in IP:
            IP.append(ip)
            po.append(65536 * [0])
            po[-1][port] = 1
            ti.append(time.time())
       #     print ti[-1], ip
        else:
            for i in range(len(IP)):
                if IP[i] == ip:
                    po[i][port] = 1
                    #print (time.time() - ti[i]), ip, "<---"
                    if (time.time() - ti[i]) < 5:        
                        p = 0
                      #  print ip, port 
                        for j in range(65536):
                            if po[i][j] == 1:
                                p = p + 1
                            else:
                                p = 0
                            if p > 14:
                                ti[i] = time.time()
                                po[i] = (65536 * [0])
                                print "Scanner detected, The scanner originated from host ", ip
                                break
                    else:
                        ti[i] = time.time()
                        po[i] = (65536 * [0])
                    
    except AttributeError:
        return

while(1):
    sniff(prn=call_back)
    

    
    