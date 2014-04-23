#!/usr/bin/env python

""" sender.py

Sender side for a TCP over UDP sender in Python.

Usage:    
 Run this file and set _FILENAME to specify file to send
 
 python sender.py

    Features:
        TCP headers
        TCP flow control
        TCP setup/teardown
        TCP checksum
        multiple packet transmission
        out of order ACK reception
        timeout based on life of oldest unacked packet
        fast resend on duplicate ACKs

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
_FILENAME = "example.jpg"
#enter as percentage from 0 to 100
corruptACK=20
dropACK=10
if len(sys.argv) > 1:
    opt2 = sys.argv[3]
    opt4 = sys.argv[4]
else:
    opt2 = "n"
    opt4 = "n"

class rTCP:

    def __init__(self,corruptACK,dropACK):
        #constants
        self.ETHERNET_MSS = 1500
        
        #states
        self.address = None
        self.ack = None
        self.seq = None
        self.acknbr = None
        self.outgoingack= None
        self.window = 0
        self.MSS = None
        self.timeout = None
        self.eldestborn = None
        #states: 1-setup 2-tx 3-teardown
        self.state = 1
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setblocking(0)
        #intentional loss options (percentages from 0 to 100)
        self.corruptACK = corruptACK
        self.dropACK = dropACK
        
    def connect(self,ip,port):
        "sets up a connection"
        #connect via udp then initiate tcp syn
        self.address=(ip,port)
        self.timeout=5 
        self.MSS = self.ETHERNET_MSS
        #generate sequence number
        self.seq = random.randint(0,9000)
        self.acknbr=0
        self.outgoingack=0
        self.ack=0
        #send SYN
        self.syn()
        
    def syn(self):
        #check state=1
        reply=0
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
            self.outgoingack=header[0]
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
        self.outgoingack=self.outgoingack+1
        pkt=self.header()
        self.socket.sendto(pkt,self.address)
        self.ack=0
        print "connected"

    def decode(self,packet):
        header = packet[0:16]
        data = packet[16:]
        
        seq,acknbr,l,flags,window,checksum=struct.unpack("!IIBBHHxx",header)
        # Corrupt the header if option 2 is selected
        if ( (opt2.lower() in ["y", "yes"]) and (random.randint(1,60) is 16) ) :
            l = l + 1
        if checksum != self.checksum(struct.pack("!IIBBH",seq,acknbr,l,flags,window)):
            print "****************************bad checksum******************************"
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
        pkt=struct.pack("!IIBBH",self.seq,self.outgoingack,self.len,flags,self.window)
        checksum = self.checksum(pkt)
        pkt=struct.pack("!IIBBHHxx",self.seq,self.outgoingack,self.len,flags,self.window,checksum)
        
        return pkt
        
    def send(self,data):
        "build packet and send data" 
        time.sleep(2)
        print "sending packet"
        if not self.state==2:
            print "Establish connection first!"
            raise
        baseseq=self.seq
        self.eldestborn = time.time()
        self.acknbr=self.seq
        while (len(data)>0) or (self.acknbr>baseseq):
            self.ack=0
            header = self.header()
            #build packet no bigger than remaining window-1 or self.MSS also at least 1 data byte
            length = min(self.window-1,self.MSS)-16
            if length<=1: #always 1 data byte
                length=1
            #launch packet - set lastsent=seq+nbr bytes sent
            if length>(len(data)-(self.seq-baseseq)):
                length=len(data)-(self.seq-baseseq)
            print "length: "+str((self.seq-baseseq,self.seq-baseseq+length,len(data)))
            packet = struct.pack("!"+str(length)+"c",*data[self.seq-baseseq:(self.seq-baseseq)+length])
            packet = header+packet
            self.window=self.window-length
            if self.window<1:
                self.window=1
            self.seq = self.seq+length
            print "outgoing: "+str((self.seq,self.outgoingack,self.window))
            if ((opt4.lower() in ["y", "yes"]) and (random.randint(1,60) is 16) ) :
                print "**************Dropped data :O ****************"
            else:
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
                    header,d = self.decode(reply)
                    print "incoming: "+str(header)
                    if header[2] is not 1:
                        raise
                    if self.acknbr < header[1]:
                        print "new ack"
                        print "old: "+str(self.acknbr)+" new: "+str(header[1])
                        # update ack number to be ack nbr
                        self.acknbr=header[1]
                        self.window=header[5]
                        #discard old data
                        del data[0:(self.acknbr-baseseq)]
                        baseseq=self.acknbr
                        if (self.acknbr>self.seq) and (len(data)<=0):
                            break
                        # if valid ack for unacked,restart timer
                        self.eldestborn = time.time()
                        self.outgoingack=header[0]+1
                        # recalc timeout
                    if self.acknbr==header[1]:
                        self.seq = self.acknbr #fast retransmit
                except:
                    pass
            if time.time() > self.eldestborn+self.timeout:  
                #if no response, check for timeout - retransmit starting at unacked seq
                print "timeout "+str((self.seq,self.acknbr))
                self.seq=self.acknbr
                self.eldestborn = time.time()
            time.sleep(0)
        print "done: "+str((self.seq,self.acknbr,len(data)))    
    def disconnect(self):
        #initiate connection teardown
        #check state==2
        reply=0
        if self.state != 2:
            print "Not connected!"
            raise
        #send FIN and get ACK
        self.state=3
        self.ack=0
        junk=1
        while junk:
            try:
                junk = self.socket.recv(1)
            except:
                junk=0
        header = self.header()
        self.socket.sendto(header,self.address)
        self.eldestborn = time.time()
        while time.time() < (self.eldestborn+self.timeout):
            try:
                reply = self.socket.recv(16)
            except:
                pass
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
            try:
                reply = self.socket.recv(16)
            except:
                pass
            if reply:
                break
        if not reply:
            print "no FIN"
            raise
        header,data = self.decode(reply)    
        if not header[4]:
            print "bad FIN: "+str(header)
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
            try:
                reply = self.socket.recv(16)
            except:
                pass
            if reply:
                self.socket.sendto(header,self.address)
                break
        print "disconnected"
        
    def sendfile(self,filename):
        "read in file, convert to list, send"
        data=list()
        with open(filename,'rb') as f:
            print "{} opened".format(filename)
            while True:
                d = f.read(1) #read one byte
                if not d:
                    break
                data.append(d)
        self.send(data)
    
    def carry(self,x,y):
        "carry and add"
        c = x + y
        return (c & 0xffff) + (c >> 16)

    def checksum(self,data):
        "compute internet checksum"
        s = 0
        for i in range(0, len(data), 2):
            w = ord(data[i]) + (ord(data[i+1]) << 8)
            s = self.carry(s, w)
        return ~s & 0xffff
        
if __name__ == "__main__":

    sender = rTCP(corruptACK,dropACK)
    
    sender.connect(HOST,PORT)
    sender.sendfile(_FILENAME)
    sender.disconnect()
