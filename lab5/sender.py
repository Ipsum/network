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
        #constants
        self.ETHERNET_MSS = 1500
        
        #states
        self.address = None
        self.ack = None
        self.seq = None
        self.acknbr = None
        self.window = 0
        self.MSS = None
        self.timeout = None
        self.eldestborn = None
        #states: 1-setup 2-tx 3-teardown
        self.state = 1
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(0)
        
    def connect(ip,port):
        "sets up a connection"
        #connect via udp then initiate tcp syn
        self.address=(ip,port)
        self.timeout=1 
        self.MSS = self.ETHERNET_MSS
        #generate sequence number
        self.seq = random.randint(0,4294967295)
        self.acknbr=0
        self.ack=0
        #send SYN
        self.syn()
        
    def syn():
        #check state=1
        if not self.state==1:
            print "Not ready to connect"
        #build packet
        self.ack=0
        pkt = self.header()
        #send SYN with seq nbr(A)
        self.socket.sendto(pkt,self.address)
        self.eldestborn = time.time()
        #get ACK as seq nbr+1(A+1) and random seq nbr(B)
        while self.eldestborn < (self.eldestborn+self.timeout):
            reply = self.socket.recv(16)
            if reply:
                break
        if not reply:
            print "no SYNACK"
            raise
        header,data = self.decode(reply)    
        if header[2]==1 and header[3]==1 and header[1]==self.seq+1: #ACK,SYN,correct acknbr
            self.acknbr=header[0]
            self.seq=header[1]
            self.window=header[5]
        else:
            print "bad SYNACK"
            raise
        #send ACK with sq numbr = received ACK(A+1) and 
        # the ACK number = received seq nbr+1(B+1)
        self.ack=1
        self.state=2
        self.acknbr=self.acknbr+1
        pkt=self.header()
        self.socket.sendto(pkt,self.address)
        self.ack=0

    def decode(self,packet):
        length = len(packet)
        header = packet[0:16]
        data = packet[16:]
        
        seq,acknbr,len,flags,window,checksum=struct.unpack("!IIBBHHxx",header)
        if checksum != crc16(struct.pack("!IIBBH",seq,acknbr,len,flags,window)):
            print "bad checksum"
            raise
        
        ACK = 1 & (flags>>4)
        SYN = 1 & (flags>>1)
        FIN = 1 & flags
        datalen=length-16
        data=struct.unpack("!"+datalen+"c",data)
        
        return (seq,acknbr,ACK,SYN,FIN,window),data
        
    def header(self):
        "build packet header"
        self.len = 4<<4 #len of packet head in 32bit words, upper half of byte
        flags = 0
        if self.state==1:
            flags |= 1<<1
        if self.ack:
            flags |= 1<<4
        if self.state==3:
            flags |= 1
        pkt=struct.pack("!IIBBH",self.seq,self.acknbr,self.len,flags,self.window)
        checksum = crc16(pkt)
        pkt=struct.pack("!IIBBHHxx",self.seq,self.acknbr,self.len,flags,self.window,checksum)
        
        return pkt
        
    def send(data):
        "build packet and send data"   
        if not self.state==2:
            print "Establish connection first!"
            raise
        lastsent=self.seq-1
        self.eldestborn = time.time()
        while data and lastsent>self.acknbr:
            self.ack=0
            header = self.header()
            #build packet no bigger than remaining window-1 or self.MSS also at least 1 data byte
            #launch packet - set lastsent=seq+nbr bytes sent
            #check for response
            # if valid ack for unacked,restart timer
            # recalc timeout
            # update ack number to be ack nbr
            #if no response, check for timeout - retransmit starting at unacked seq
    def disconnect():
        #initiate connection teardown
        #check state==2
        #send FIN and get ACK
        #get FIN and send ACK
        #for 30 seconds, respond to anything with ACK
        #done
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