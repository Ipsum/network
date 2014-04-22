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

HOST, PORT = "localhost", 9999

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
        
    def connect(self,ip,port):
        "sets up a connection"
        #connect via udp then initiate tcp syn
        self.address=(ip,port)
        self.timeout=1 
        self.MSS = self.ETHERNET_MSS
        #generate sequence number
        self.seq = random.randint(0,9000)
        self.acknbr=0
        self.ack=0
        #send SYN
        self.syn()
        
    def syn(self):
        #check state=1
        if not self.state==1:
            print "Not ready to connect"
        #build packet
        self.ack=0
        pkt = self.header()
        #send SYN with seq nbr(A)
        self.socket.setblocking(1)
        self.socket.sendto(pkt,self.address)
        self.socket.setblocking(0)
        print "connecting...."
        self.eldestborn = time.time()
        #get ACK as seq nbr+1(A+1) and random seq nbr(B)
        while time.time() < (self.eldestborn+self.timeout):
            try:
                reply = self.socket.recv(16)
            except:
                sys.exc_clear()
                pass
        if not reply:
            print "no SYNACK"
            raise
        print "SYNACK"
        header,data = self.decode(reply)    
        if header[2]==1 and header[3]==1 and header[1]==self.seq+1: #ACK,SYN,correct acknbr
            self.acknbr=header[0]
            self.seq=header[1]
            self.window=header[5]
        else:
            print "bad SYNACK: "+str(header)
            raise
        #send ACK with sq numbr = received ACK(A+1) and 
        # the ACK number = received seq nbr+1(B+1)
        self.ack=1
        self.state=2
        self.acknbr=self.acknbr+1
        pkt=self.header()
        self.socket.sendto(pkt,self.address)
        self.ack=0
        print "connected"

    def decode(self,packet):
        header = packet[0:16]
        data = packet[16:]
        
        seq,acknbr,l,flags,window,checksum=struct.unpack("!IIBBHHxx",header)
        if checksum != self.crc16(struct.pack("!IIBBH",seq,acknbr,l,flags,window)):
            print "bad checksum"
            raise
        
        ACK = 1 & (flags>>4)
        SYN = 1 & (flags>>1)
        FIN = 1 & flags
        datalen=len(data)
        data=struct.unpack("!"+str(datalen)+"c",data)
        
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
        checksum = self.crc16(pkt)
        pkt=struct.pack("!IIBBHHxx",self.seq,self.acknbr,self.len,flags,self.window,checksum)
        
        return pkt
        
    def send(self,data):
        "build packet and send data"   
        print "sending packet"
        if not self.state==2:
            print "Establish connection first!"
            raise
        baseseq=self.seq
        self.eldestborn = time.time()
        print self.seq
        print self.acknbr
        while data or self.seq>self.acknbr:
            self.ack=0
            header = self.header()
            #build packet no bigger than remaining window-1 or self.MSS also at least 1 data byte
            length = min(self.window-1,self.MSS)-16
            if length<=1: #always 1 data byte
                length=1
            #launch packet - set lastsent=seq+nbr bytes sent
            if length>len(data):
                length=len(data)
            packet = struct.pack("!"+str(length)+"c",*data[self.seq-baseseq:(self.seq-baseseq)+length])
            packet = header+packet
            self.window=self.window-length
            self.seq = self.seq+length+1
            print "outgoing: "+str((self.seq,self.acknbr,self.window))
            self.socket.sendto(packet,self.address)
            #check for response
            reply=0
            try:
                reply = self.socket.recv(16)
            except:
                sys.exc_clear()
                pass
            #get ACK as seq nbr+1(A+1) and random seq nbr(B)
            if reply:
                try:
                    header,data = self.decode(reply)
                    print "incoming: "+str(header)
                    if header[2] is not 1:
                        raise
                    if self.acknbr < header[1]:
                        # update ack number to be ack nbr
                        self.acknbr=header[1]
                        self.window=header[5]
                        # if valid ack for unacked,restart timer
                        self.eldestborn = time.time()
                        # recalc timeout
                except:
                    pass
            if time.time() > self.eldestborn+self.timeout:  
                #if no response, check for timeout - retransmit starting at unacked seq
                self.seq=self.acknbr
                self.eldestborn = time.time()
                
    def disconnect(self):
        #initiate connection teardown
        #check state==2
        if self.state != 2:
            print "Not connected!"
            raise
        #send FIN and get ACK
        self.state=3
        self.ack=0
        header = self.header()
        self.socket.sendto(header,self.address)
        self.eldestborn = time.time()
        while time.time() < (self.eldestborn+self.timeout):
            reply = self.socket.recv(16)
            if reply:
                break
        if not reply:
            print "no FIN-ACK"
            raise
        header,data = self.decode(reply)    
        if not header[2]:
            print "bad FIN-ACK"
            raise
        #get FIN and send ACK
        self.eldestborn = time.time()
        while time.time() < (self.eldestborn+self.timeout):
            reply = self.socket.recv(16)
            if reply:
                break
        if not reply:
            print "no FIN"
            raise
        header,data = self.decode(reply)    
        if not header[4]:
            print "bad FIN"
            raise
        self.ack=1
        self.state=2
        header=self.header()
        self.socket.sendto(header,self.address)
        #for 30 seconds, respond to anything with ACK
        #done
        self.state=1
        self.ack=0
        self.eldestborn=time.time()
        while time.time() < (self.eldestborn+30):
            reply = self.socket.recv(16)
            if reply:
                self.socket.sendto(header,self.address)
            
    def sendfile(self,filename):
        "read in file, convert to list, send"
        data=[]
        with open(filename,'rb') as f:
            print "{} opened".format(filename)
            while True:
                d = f.read(1) #read one byte
                if not d:
                    break
                data.append(d)
        self.send(data)
    
    def swap_bytes(self,word_val):
        """swap lsb and msb of a word"""
        msb = word_val >> 8
        lsb = word_val % 256
        return (lsb << 8) + msb   
    
    def crc16(self,data):
        """Calculate the CRC16 of a datagram"""
        crc = 0xFFFF
        for i in data:
            crc = crc ^ ord(i)        
            for j in xrange(8):
                tmp = crc & 1
                crc = crc >> 1
                if tmp:
                    crc = crc ^ 0xA001
        return self.swap_bytes(crc)        
if __name__ == "__main__":
    sender = rTCP()
    sender.connect(HOST,PORT)
    sender.sendfile("example.jpg")
   # try:
   #     sender.connect(HOST,PORT)
   #     sender.sendfile("example.jpg")
   #     sender.disconnect()
   # except:
   #     print "there was a problem!"