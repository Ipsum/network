# -------- C l i e n t . p y -------- #
# Author: Andrew Hajj
# Email: andrew.hajj@gmail.com
# Credits: David Tyler, Andrew Hajj
# Date: 2/1/14
# Source:   Code was built off of
#           "http://docs.python.org/2/library/socketserver.html",
#           but holds little similarity now.
#           CRC16 table based off code found in the CRC library found at
#           'https://github.com/gennady/pycrc16/blob/master/python2x/crc16/crc16pure.py"
# Purpose: Client side for a UDP server in Python.  Can send and receive files
#          (under 10kB works best, as found from tests)
# Usage:    Run this file and use gui to specify file to send/receive and the server details
#           ex. 'python client.py'
#
# ******** UPDATED 3/09/14 ***********
# Client now provides reliable transer (RTD 2.2)
#
# ******** UPDATED 2/13/14 ***********
# Now splits the file in to 1kb packets to be sent over to the server
# Size of the packets can be changed by modifying the buffer

import socket
import sys
import time
import os
import struct
import random
#import bitarray

from Tkinter import *
from ttk import *

#HOST, PORT = "cato.ednos.net", 4422
HOST, PORT = "localhost", 9999

# Size of the packets to be sent
packet_size = 1024
buf = 1024

def swap_bytes(word_val):
    """swap lsb and msb of a word"""
    msb = word_val >> 8
    lsb = word_val % 256
    return (lsb << 8) + msb   
    
def crc16(data):
    """Calculate the CRC16 of a datagram"""
    crc = 0xFFFF
    for i in data:
        crc = crc ^ ord(i)        
        for j in xrange(8):
            tmp = crc & 1
            crc = crc >> 1
            if tmp:
                crc = crc ^ 0xA001
    return swap_bytes(crc)  
    
class GUI:
    def __init__(self,master):
        """initial menu setup"""
        self.master = master
        #create menu
        menubar = Menu(self.master)
        self.master['menu'] = menubar
        menu_file = Menu(menubar)
        menu_file.add_command(label='Exit', command=self.exitcmd)
        #communications settings
        Label(master, text="Address").grid(row=0,column=0)
        Label(master, text="Port").grid(row=1,column=0)
        self.addr = StringVar()
        Entry(master,textvariable=self.addr).grid(row=0,column=1)
        self.port = StringVar()
        Entry(master,textvariable=self.port).grid(row=1,column=1)
        
        self.addr.set(HOST)
        self.port.set(str(PORT))
        
        #send file elements
        self.fname = StringVar()
        Label(master, text="File name").grid(row=2,column=1)
        Entry(master,textvariable=self.fname).grid(row=2,column=0)
        
        # Checkboxes for Options 2 and 3
        self.varOptTwo = IntVar()
        Checkbutton(master, text='Option 2', variable=self.varOptTwo).grid(row=3,column=0)
        self.varOptThree = IntVar()
        Checkbutton(master, text='Option 3', variable=self.varOptThree).grid(row=3,column=1)
        
        Button(master,text="Send File",command=self.send).grid(row=4,column=0)
#        Button(master,text="Get File",command=self.get).grid(row=4,column=1)

        #state machine diagram
        self.states = [PhotoImage(file='state1.gif'),PhotoImage(file='state2.gif'),
        PhotoImage(file='state3.gif'),PhotoImage(file='state4.gif')]
        
        self.state=Label(master,image=self.states[0])
        self.state.image=self.states[0]
        self.state.grid(row=5,column=0,columnspan=2)
        
        self.progress = Progressbar(master,orient=HORIZONTAL,length=200,mode='determinate')
        self.progress.grid(row=6,columnspan=2)
        
    def sendPkt(self,packet, OptTwo):
        "send the packet"
        self.sock.send(packet)
        sys.stdout.write('.')
        time.sleep(.15)
        
        #wait for ack
        #ack for packet #0: 0x00
        #ack for packet #1: 0xFF
        
        ack_message = self.sock.recv(3)
        ack_message = struct.unpack("!?H",ack_message)
        
        # If Option two is selected, intentionally corrupt the ACK packet
        # then recover it.  Added some randomness in there was well
        if OptTwo is 1:
            randVar = random.randint(1,60)
            if randVar == 32:
                ack_message = (not ack_message[0], ack_message[1])
        if ((ack_message[0] != struct.unpack("!?1021cH",packet)[0]) or 
        (ack_message[1] != crc16(struct.pack("!?",ack_message[0])))):
            sys.stdout.write("resending(corrupted packet)")
            self.sendPkt(packet, OptTwo)
        
    def send(self):
        "Send a file" 
        #socket stuff
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5)
        host = self.addr.get()
        port = int(self.port.get())
        
        #option variables
        OptionTwoVar = self.varOptTwo.get()
        OptionThreeVar = self.varOptThree.get()
        
        #connect
        self.sock.connect((host, port))
        
        filename = self.fname.get()
        print "Checking if {} exists".format(filename)

        #Check to make sure the file actually exists
        check = os.path.isfile(filename)
        if check is True:

            # Counter is sent along with the packet so that the server 
            # knows which packet state it is.  It is inverted after each 
            # successful packet send
            counter = int(0)
            self.state.image=self.states[0]
            # Initiate the ACK packet to be blank
            ack_message = ""
            data = []
            # read entire file into list of bytes
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
            if OptionThreeVar is 1:
                data.insert(0, "C")
            else:
                data.insert(0,"N")
            data.insert(0,"_")            
            # Append the file name to the beginning of the data stream
            while(d):
                data.insert(0,d.pop())

            maxstep = len(data)
            self.progress["maximum"] = maxstep
            sys.stdout.write('Sending...')
            while(len(data)>1021):
            
                #step progress bar
                self.progress["value"]=maxstep-len(data)
                self.master.update()
                
                # Now, we build the packet
                # Packet format:
                # [|id: 1 byte|data: 1021 bytes|crc: 2 bytes|]
                # 1024 bytes total, 1024*8 bits
                pktdata = data[0:1021]
                del data[0:1021]
                
                # Pack the counter and data to make a checksum out of it
                pkt=struct.pack("!?1021c",counter,*pktdata)
                
                # Create a 2 byte checksum
                checksum = crc16(pkt)

                #build packet with checksum
                pkt=struct.pack("!?1021cH",counter,*pktdata+[checksum])
                #send packet
                if counter:
                    self.state.configure(image=self.states[3])
                    self.state.image = self.states[3]
                else:
                    self.state.configure(image=self.states[1])
                    self.state.image = self.states[1]
                self.master.update()
                self.sendPkt(pkt, OptionTwoVar)
                if counter:
                    self.state.configure(image=self.states[0])
                    self.state.image = self.states[0]
                else:
                    self.state.configure(image=self.states[2])
                    self.state.image = self.states[2]
                self.master.update()
                counter = not counter
            #send last packet
            pkt=struct.pack("!?"+str(len(data))+"c"+str(1021-len(data))+"x",counter,
                    *data)

            checksum = crc16(pkt)
            pkt=struct.pack("!?"+str(len(data))+"c"+str(1021-len(data))+"xH",counter,
                    *data+[checksum])
            
            if counter:
                self.state.image=self.states[3]
            else:
                self.state.image=self.states[1]
            self.master.update()
            self.sendPkt(pkt, OptionTwoVar)
            self.state.image=self.states[0]
            self.master.update()
        else:
            print "Invalid File"

        self.sock.close()

    def get(self):
        "Get a file"
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(10)
        host = self.addr.get()
        port = int(self.port.get())
        self.sock.connect((host, port))
        
        print "Requesting", self.fname.get()+"..."
        # Create a new file
        try:
            file = open(self.fname.get(), 'wb')
        except:
            print "There was a problem saving the file..."

        # Send the name of the file to be pulled from the server
        self.sock.send(self.fname.get())

        return_message = self.sock.recv(packet_size)
        #print return_message
        if "not found" in return_message:
            print "{} not found".format(self.fname.get())
        else:
            print "Creating {} from server...".format(return_message)
        
            # Now get and write the data (in 1kb packets)
            data = self.sock.recv(buf + sys.getsizeof(self.fname.get()+" "))
            sys.stdout.write('Receiving...')
            try:
                counter = 1
                while(data):
                    # Parse the packet
                    recievedFileName, sep, data = data.partition(" ")
                    packet_counter, sep, data = data.partition("_")
                    # Checksum is stored as the last four char in the string
                    received_checksum = data[-4:]
                    # Strip the checksum from data
                    data = data[:-4]
                    # Check to see if checksum adds up
                    if received_checksum is crc16(data) and counter is packet_counter:
                        # Write that packet to the file
                        file.write(data)
                        self.sock.send("Packet received")
                        time.sleep(.15)
                        counter = counter + 1
                    sys.stdout.write('.')
                    #Receive the next packet to be saved to the file
                    data = self.sock.recv(buf + sys.getsizeof(self.fname.get()+" "))
            except socket.timeout:
                print "Done!"
                print "***    Received file: {}   ***".format(recievedFileName)

            file.close()
        self.sock.close()
        
    def exitcmd(self):
        "closes program"
        os._exit(99) #unconditional shutdown signal
        
if __name__ == "__main__":
    #setup gui stuff
    root = Tk()
    sty = Style()
    sty.configure('.', font='helvetica 15')
    sty.configure('Tab', font='helvetica 8 bold')
    root.title("Lab 3")
    root.option_add('*tearOff', FALSE)
    GUI(root)
    root.mainloop()
