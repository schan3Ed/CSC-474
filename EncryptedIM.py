#!/usr/bin/python

#Original Author : Henry Tan

import os
import sys
import argparse
import socket
import select
import logging
import signal #To kill the programs nicely
import random
import Crypto.Cipher.AES as AES
import Crypto.Hash.SHA256 as SHA256
import hashlib
import hmac

from collections import deque

############
#GLOBAL VARS
DEFAULT_PORT = 9999
s = None
server_s = None
logger = logging.getLogger('main')
###########
def encrypt(akey, ckey, data):
    for i in range(16 - len(data) % 16):
      data += "\n"
    IV = os.urandom(16)
    en = AES.new(ckey, AES.MODE_CBC, IV)
    d = en.encrypt(data)
    h = hmac.new(akey, d, SHA256).digest()[0:32]
  #  print len(h), " ", len(d), " ", len(IV)
 #   print h
    return IV + h + d

def decrypt(data, akey, ckey):
    IV = data[0:16]
    h = data[16:48]
    data = data[48:]
#    print len(data)
    de = AES.new(ckey, AES.MODE_CBC, IV)
    c = hmac.new(akey, data, SHA256).digest()[0:32]
    if hmac.compare_digest(c, h) == False:
        print "Message has been changed. Channel unsafe"
        return ''
    b = de.decrypt(data)
    b = b.translate(None, "\n")
    b += "\n"
    return b


def parse_arguments():
  parser = argparse.ArgumentParser(description = 'A P2P IM service.')
  parser.add_argument('-c', dest='connect', metavar='HOSTNAME', type=str,
    help = 'Host to connect to')
  parser.add_argument('-s', dest='server', action='store_true',
    help = 'Run as server (on port 9999)')
  parser.add_argument('-authkey', dest='akey',metavar='AKEY',  type=str,
    help = 'Authentication key for hmac')   
  parser.add_argument('-confkey', dest='ckey', metavar='CKEY', type=str,
    help = 'Encryption key')
  parser.add_argument('-p', dest='port', metavar='PORT', type=int, 
    default = DEFAULT_PORT,
    help = 'For testing purposes - allows use of different port')

  return parser.parse_args()

def print_how_to():
  print "This program must be run with exactly ONE of the following options"
  print "-c <HOSTNAME>  : to connect to <HOSTNAME> on tcp port 9999"
  print "-s             : to run a server listening on tcp port 9999"
  print "-authkey       : authentication key used for authenticating messages"
  print "-confkey       : conf key used for encrypting messages"

def sigint_handler(signal, frame):
  logger.debug("SIGINT Captured! Killing")
  global s, server_s
  if s is not None:
    s.shutdown(socket.SHUT_RDWR)
    s.close()
  if server_s is not None:
    s.close()

  quit()

def init():
  global s
  args = parse_arguments()
  logging.basicConfig()
  logger.setLevel(logging.CRITICAL)
  akey = hashlib.sha256(args.akey).digest()[0:32]
  ckey = hashlib.sha256(args.ckey).digest()[0:32]
  #Catch the kill signal to close the socket gracefully
  signal.signal(signal.SIGINT, sigint_handler)

  if args.connect is None and args.server is False:
    print_how_to()
    quit()

  if args.connect is not None and args.server is not False:
    print_how_to()
    quit() 

  if args.connect is not None:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    logger.debug('Connecting to ' + args.connect + ' ' + str(args.port))
    s.connect((args.connect, args.port))
  #  print len(akey + ckey)
  #  s.send(akey + ckey)

  if args.server is not False:
    global server_s
    server_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_s.bind(('', args.port))
    server_s.listen(1) #Only one connection at a time
    s, remote_addr = server_s.accept()
    server_s.close()
  #  keys = s.recv(64)
    #if keys == akey + ckey:
     # print len("Keys are valid, connection establised.\n")
  #    s.send(encrypt(akey, ckey, "Keys are valid, connection establised.\n"))
  #  else:
      #print len("Keys are invalid, terminate connection\n")
   #   s.send("Keys are invalid, terminate connection\n")
    #  s.close()
   #   sys.exit()
    logger.debug("Connection received from " + str(remote_addr))

def main():
  args = parse_arguments()
  global s
  datalen=64
  akey = hashlib.sha256(args.akey).digest()[0:32]
  ckey = hashlib.sha256(args.ckey).digest()[0:32]
  init()
  
  inputs = [sys.stdin, s]
  outputs = [s]

  output_buffer = deque()

  while s is not None: 
    #Prevents select from returning the writeable socket when there's nothing to write
    if (len(output_buffer) > 0):
      outputs = [s]
    else:
      outputs = []

    readable, writeable, exceptional = select.select(inputs, outputs, inputs)

    if s in readable:
      data = s.recv(1024)
      #print "received packet, length "+str(len(data))
      if ((data is not None) and (len(data) > 0)):
        data = decrypt(data, akey, ckey)
        sys.stdout.write(data) #Assuming that stdout is always writeable
      else:
        #Socket was closed remotely
        s.close()
        s = None

    if sys.stdin in readable:
      data = sys.stdin.readline(1024 - 64)
      if(len(data) > 0):
        output_buffer.append(data)
      else:
        #EOF encountered, close if the local socket output buffer is empty.
        if( len(output_buffer) == 0):
          s.shutdown(socket.SHUT_RDWR)
          s.close()
          s = None

    if s in writeable:
      if (len(output_buffer) > 0):
        data = output_buffer.popleft()
      #  print len(data)
        data = encrypt(akey, ckey, data)
      #  print len(data)
        bytesSent = s.send(data)
        #If not all the characters were sent, put the unsent characters back in the buffer
        if(bytesSent < len(data)):
        #  print "here"
          output_buffer.appendleft(data[bytesSent:])

    if s in exceptional:
      s.shutdown(socket.SHUT_RDWR)
      s.close()
      s = None

###########

if __name__ == "__main__":
  main()
