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
    
    def handle(self):
        "extract and read packet header"
        #determine if SYN, data, FIN or ACK
        self.socket = self.request[1]
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
        
    def syn(self,header):
        #generate a random seq nbr
        #respond with SYN=1, random seq nbr, ack=incoming seq+1,windowsize
        #set state indicating that we still need an ack in the save function
        #create new file
    def fin(self,header):
        #check that connection is in an open state
        #send an ACK
        #send a FIN and get ACK - close connection
    def save(self,header,data):
        #check state - if in state one, move to state 2 on ACK otherwise nothing
        #if in state 2, process data
        #check seq number = current ack value otherwise resend current ack value
        #adjust window size
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