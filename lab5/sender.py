#!/usr/bin/env python

""" sender.py

Sender side for a UDP server in Python.  Can send files in 1 kb packets.

Usage:    
 Run this file and use gui to specify file to send/receive and the server details
 
 python sender.py
 
Sender now provides reliable transfer even if there is a packet loss (RDT 3.0)

CRC16 table based off code found in the CRC library found at
 'https://github.com/gennady/pycrc16/blob/master/python2x/crc16/crc16pure.py"
"""

import socket
import sys
import time
import struct
import random

__author__ = "David Tyler"
__credits__ = ["Andrew Hajj", "David Tyler"]
__license__ = "MIT"
__email__ = "dtyler@gmail.com"
__status__ = "Development"

class rTCP:

    def __init__(self):
        self.address = None
        self.seq = None
        self.ack = None
        self.window = None
        self.timeout = None
        #states: 1-setup 2-tx 3-teardown
        self.state = 1
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    def connect(ip,port,window):
        "sets up a connection"
        #connect via udp then initiate tcp syn
        self.address=(ip,port)
        self.window = window
        #generate sequence number
        self.seq = random.randint(0,4294967295)
        #send SYN
        self.syn()
        self.state = 2
    def syn():
        #check state=1
        #build packet
        #send SYN with seq nbr(A)
        #get ACK as seq nbr+1(A+1) and random seq nbr(B)
        #send ACK with sq numbr = received ACK(A+1) and 
        # the ACK number = received seq nbr+1(B+1)
        
    def send(data):
        "build packet and send data"   
        if not self.state==2:
            print "Establish connection first!"
            return
        
    def disconnect():
        #initiate connection teardown
        #check state
        #send FIN
        #get FIN & ACK
        #send ack
        self.state=1
    def sendfile(filename):
        "read in file, convert to list, send"
        with open(filename,'rb') as f:
            print "{} opened".format(self.fname.get())
            while True:
                d = f.read(1) #read one byte
                if not d:
                    break
                data.append(d)

        # Make the file name into a list
        d=list("new_"+filename)
        data.insert(0,"_")
        while(d):
            data.insert(0,d.pop())