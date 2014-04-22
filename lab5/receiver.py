#!/usr/bin/env python

""" receiver.py

 A simple UDP server to receive and send files over the internet

 Usage:
  Run this file with arguments for the ip and self.socket to bind to.

  python receiver.py cato.ednos.net 4422


 Files are saved and served from same directory as this script.
 Files are sent and received in the format: filename binaryfiledata
 Example test.txt:
  test.txt this is a test file

"""

import SocketServer
import sys
import time
import struct
import random

__author__ = "David Tyler"
__credits__ = ["Andrew Hajj", "David Tyler"]
__license__ = "MIT"
__email__ = "dtyler@gmail.com"
__status__ = "Development"

class MyUDPHandler(SocketServer.BaseRequestHandler):
    "UDP server class to handle incoming data and return response"
    
    def configure(self,window):
        "configure server before running"
        self.maxwindow=window
        
    def handle(self):
        "extract and read packet header"
        #determine if SYN, data, FIN or ACK
        self.address = self.request[1]
        data=self.request[0]
        header,data=self.decode(data)
        if header[3]:
            self.syn(header)
        elif header[4]:
            self.fin(header)
        else:
            self.save(header,data)
        
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
        
    def syn(self,header):
        #generate a random seq nbr
        self.seq = random.randint(0,4294967295)
        #respond with SYN=1, random seq nbr, ack=incoming seq+1,windowsize
        self.acknbr=header[0]+1
        self.state=1
        self.window=self.maxwindow
        self.ack=0
        header = self.header()
        socket.sendto(header,self.address)
        #set state indicating that we still need an ack in the save function
        self.state=1
        #create new file
        self.createfile("received.jpg","")
        
    def fin(self,header):
        #check that connection is in an open state
        if self.state==3:
            #check for ACK and close connection
            if header[
        if self.state==2:
            #send an ACK
            self.ack=1
            pkt=self.header()
            socket.sendto(pkt,self.address)
            #send a FIN
            self.state=3
            self.ack=0
            pkt=self.header()
            socket.sendto(pkt,self.address)
        else:
            return
            
    def save(self,header,data):
        #check state - if in state one, move to state 2 on ACK otherwise nothing
        if self.state==1:
            if header[2]:
                self.state=2
            return
            
        if self.state==3:
            if header[2]:
                #close connection
                self.state=1
            return
        #if in state 2, process data
        if self.state != 2:
            return
        #check seq number = current ack value otherwise resend current ack value
        if not header[0] = self.acknbr:
            self.ack=1
            #save packet? and modify window size
            pkt = self.header()
            socket.sendto(pkt,self.address)
            return
        #check for saved packets and adjust window size
        #save data by append to file made in syn
        #send ack with received seq+bytesrecv+1 as acknbr,incoming ack as seq nbr
    def savefile(self, filename, data):
        "Save file that was sent to this server via UDP self.socket"
        # Appends the data to the end of the file.
        # Used for the second packet on for a file
        try:
            f = open(filename, 'ab')
        except:
            return False
        f.write(data)
        f.close()
        return True 
        
    def createfile(self, filename, data):
        "Overwrite existing file if we get a file by the same name"
        # Used for the first packet of a file.
        # Creates a new file of the specified name
        try:
            f = open(filename, 'wb')
            f.write(data)
        except:
            pass
            #self.socket.sendto("could not erase old file", self.client_address)
        f.close()
        return True
        
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