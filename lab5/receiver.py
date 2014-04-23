#!/usr/bin/env python

""" receiver.py

 A simple TCP over UDP server to receive and send files over the internet

 Usage:
  Run this file with arguments for the ip and self.socket to bind to.

  python receiver.py cato.ednos.net 4422 corrupt% drop %


 Files are saved and served from same directory as this script as _FILENAME.
 Features:
    TCP headers
    TCP flow control
    TCP setup/teardown
    TCP checksum
    packet reordering

"""

import SocketServer
import sys
import time
import struct
import random
import socket

__author__ = "David Tyler"
__credits__ = ["Andrew Hajj", "David Tyler"]
__license__ = "MIT"
__email__ = "dtyler@gmail.com"
__status__ = "Development"

_HOST = "localhost"
_PORT = 9999
_FILENAME = "received.jpg"

maxwindow=3000
window=3000
futurepackets=dict()
seq=0
acknbr=0
ack=0
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

if len(sys.argv) > 1:
    opt3 = int(sys.argv[3])
    opt5 = int(sys.argv[4])
else:
    opt3 = 0
    opt5 = 0

class Globals():
    "handles state of server"
    def __init__(self):
        state=0
        
class MyUDPHandler(SocketServer.BaseRequestHandler):
    "UDP server class to handle incoming data and return response"
    
    global maxwindow
    global window
    global futurepackets
    global seq
    global acknbr
    global ack
    global socket
    
    def handle(self):
        "extract and read packet header"
        #determine if SYN, data, FIN or ACK
        self.address = self.request[1]
        try:
            header,data=self.decode(self.request[0])
        except:
            return
        print "in: "+str((header[0],header[1],header[2]))
        if header[3]:
            print "SYN"
            self.syn(header)
        elif header[4]:
            print "FIN"
            self.fin(header)
        else:
            if (random.randint(0,99)<opt5):
                print "**************Dropped data :O ****************"
            else:
                print "DATA"
                self.save(header,data)
        
    def decode(self,packet):
        header = packet[0:16]
        data = packet[16:]
        seq,acknbr,l,flags,window,checksum=struct.unpack("!IIBBHHxx",header)   
        # Corrupt the header if option 3 is selected
        if (random.randint(0,99)<opt3):
            l = l + 1
        if checksum != self.checksum(struct.pack("!IIBBH",seq,acknbr,l,flags,window)):
            print "****************************bad checksum******************************"
            raise Exception("bad checksum")
        ACK = 1 & (flags>>4)
        SYN = 1 & (flags>>1)
        FIN = 1 & flags
        datalen=len(data)
        data=struct.unpack("!"+str(datalen)+"c",data)
        
        return (seq,acknbr,ACK,SYN,FIN,window),data
        
    def header(self):
        "build packet header"
        global maxwindow
        global window
        global futurepackets
        global seq
        global acknbr
        global ack
        global socket
        len = 4<<4 #len of packet head in 32bit words, upper half of byte
        flags = 0
        if globals.state==1:
            flags |= 1<<1
        if ack:
            flags |= 1<<4
        if globals.state==3:
            flags |= 1
        print "flags: "+str(flags)
        pkt=struct.pack("!IIBBH",seq,acknbr,len,flags,window)
        checksum = self.checksum(pkt)
        pkt=struct.pack("!IIBBHHxx",seq,acknbr,len,flags,window,checksum)
        
        return pkt        
        
    def syn(self,header):
        global maxwindow
        global window
        global futurepackets
        global seq
        global acknbr
        global ack
        global socket
        global _FILENAME
        #generate a random seq nbr
        seq = random.randint(0,9000)
        #respond with SYN=1, random seq nbr, ack=incoming seq+1,windowsize
        acknbr=header[0]+1
        globals.state=1
        window=maxwindow
        ack=1
        header = self.header()
        print "ACK:"+str((seq,acknbr,ack,window))
        socket.sendto(header,self.client_address)
        #set state indicating that we still need an ack in the save function
        globals.state=1
        #create new file
        self.createfile(_FILENAME,"")
        
    def fin(self,header):
        global maxwindow
        global window
        global futurepackets
        global seq
        global acknbr
        global ack
        global socket
        #check that connection is in an open globals.state
        if globals.state==2:
            #send an ACK
            ack=1
            pkt=self.header()
            socket.sendto(pkt,self.client_address)
            #send a FIN
            globals.state=3
            ack=0
            pkt=self.header()
            print "sending FIN: "+str((seq,acknbr,globals.state))
            socket.sendto(pkt,self.client_address)
            #reset the receiver
            window=maxwindow
            futurepackets.clear()
            futurepackets=dict()
            print "connection closed"
        else:
            return
            
    def save(self,header,data):
        global maxwindow
        global window
        global futurepackets
        global seq
        global acknbr
        global ack
        global socket
        global _FILENAME
        #check state - if in state one, move to state 2 on ACK otherwise nothing
        if globals.state==1:
            if header[2]:
                globals.state=2
            return
            
        if globals.state==3:
            if header[2]:
                #close connection
                globals.state=0
            return
        #if in state 2, process data
        if globals.state != 2:
            return
        #check seq number = current ack value otherwise resend current ack value
        if not header[0] == acknbr:
            ack=1
            print "mismatched seq: "+str((header[0],acknbr))
            #check for space
            if len(data)<=window:
                #save packet and modify window size
                futurepackets[header[0]]=data
                window = maxwindow-sys.getsizeof(futurepackets.values())
            #resend old ack
            seq=header[1]
            pkt = self.header()
            print "out1: "+str((seq,acknbr))
            socket.sendto(pkt,self.client_address)
            return
        acknbr=header[0]+len(data)
        #check for saved packets and adjust window size
        try:
            data=data+futurepackets[acknbr]
            del futurepackets[acknbr]
            window = maxwindow-sys.getsizeof(futurepackets.values())
            acknbr=header[0]+len(data)
        except:
            pass
        #save data by append to file made in syn
        self.savefile(_FILENAME,data)
        #send ack with received seq+bytesrecv+1 as acknbr,incoming ack as seq nbr
        ack=1
        seq=header[1]
        pkt=self.header()
        print "matched seq: "+str((seq,acknbr,ack,window))
        print "out2: "+str((seq,acknbr))
        socket.sendto(pkt,self.client_address)
        #check for old saved packets and discard
        for key in futurepackets.keys():
            if key<acknbr:
                del futurepackets[key]
                window = maxwindow-sys.getsizeof(futurepackets.values())
                
    def savefile(self, filename, data):
        "Save file that was sent to this server via UDP self.socket"
        # Appends the data to the end of the file.
        # Used for the second packet on for a file
        print "saving to file..."
        data = ''.join(data)
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
        
    def carry(self,x,y):
        "carry and add"
        c = x + y
        return (c & 0xffff) + (c >> 16)

    def checksum(self,data):
        "compute 1's complement"
        s = 0
        for i in range(0, len(data), 2):
            w = ord(data[i]) + (ord(data[i+1]) << 8)
            s = self.carry(s, w)
        return ~s & 0xffff
        
if __name__ == "__main__":
    try:
        HOST, PORT = sys.argv[1], int(sys.argv[2])
    except:
        HOST, PORT = _HOST, int(_PORT)

    globals = Globals()
    print "Running on "+HOST+":"+str(PORT)
    server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    server.serve_forever()