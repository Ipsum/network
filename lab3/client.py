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
#import bitarray

from Tkinter import *
from ttk import *

#HOST, PORT = "cato.ednos.net", 4422
HOST, PORT = "localhost", 9999

# Size of the packets to be sent
packet_size = 1024
buf = 1024

# Code for CRC (used in the Checksum)
# 32 by 8 CRC table 
CRC16_TABLE = [
        0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50a5, 0x60c6, 0x70e7,
        0x8108, 0x9129, 0xa14a, 0xb16b, 0xc18c, 0xd1ad, 0xe1ce, 0xf1ef,
        0x1231, 0x0210, 0x3273, 0x2252, 0x52b5, 0x4294, 0x72f7, 0x62d6,
        0x9339, 0x8318, 0xb37b, 0xa35a, 0xd3bd, 0xc39c, 0xf3ff, 0xe3de,
        0x2462, 0x3443, 0x0420, 0x1401, 0x64e6, 0x74c7, 0x44a4, 0x5485,
        0xa56a, 0xb54b, 0x8528, 0x9509, 0xe5ee, 0xf5cf, 0xc5ac, 0xd58d,
        0x3653, 0x2672, 0x1611, 0x0630, 0x76d7, 0x66f6, 0x5695, 0x46b4,
        0xb75b, 0xa77a, 0x9719, 0x8738, 0xf7df, 0xe7fe, 0xd79d, 0xc7bc,
        0x48c4, 0x58e5, 0x6886, 0x78a7, 0x0840, 0x1861, 0x2802, 0x3823,
        0xc9cc, 0xd9ed, 0xe98e, 0xf9af, 0x8948, 0x9969, 0xa90a, 0xb92b,
        0x5af5, 0x4ad4, 0x7ab7, 0x6a96, 0x1a71, 0x0a50, 0x3a33, 0x2a12,
        0xdbfd, 0xcbdc, 0xfbbf, 0xeb9e, 0x9b79, 0x8b58, 0xbb3b, 0xab1a,
        0x6ca6, 0x7c87, 0x4ce4, 0x5cc5, 0x2c22, 0x3c03, 0x0c60, 0x1c41,
        0xedae, 0xfd8f, 0xcdec, 0xddcd, 0xad2a, 0xbd0b, 0x8d68, 0x9d49,
        0x7e97, 0x6eb6, 0x5ed5, 0x4ef4, 0x3e13, 0x2e32, 0x1e51, 0x0e70,
        0xff9f, 0xefbe, 0xdfdd, 0xcffc, 0xbf1b, 0xaf3a, 0x9f59, 0x8f78,
        0x9188, 0x81a9, 0xb1ca, 0xa1eb, 0xd10c, 0xc12d, 0xf14e, 0xe16f,
        0x1080, 0x00a1, 0x30c2, 0x20e3, 0x5004, 0x4025, 0x7046, 0x6067,
        0x83b9, 0x9398, 0xa3fb, 0xb3da, 0xc33d, 0xd31c, 0xe37f, 0xf35e,
        0x02b1, 0x1290, 0x22f3, 0x32d2, 0x4235, 0x5214, 0x6277, 0x7256,
        0xb5ea, 0xa5cb, 0x95a8, 0x8589, 0xf56e, 0xe54f, 0xd52c, 0xc50d,
        0x34e2, 0x24c3, 0x14a0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
        0xa7db, 0xb7fa, 0x8799, 0x97b8, 0xe75f, 0xf77e, 0xc71d, 0xd73c,
        0x26d3, 0x36f2, 0x0691, 0x16b0, 0x6657, 0x7676, 0x4615, 0x5634,
        0xd94c, 0xc96d, 0xf90e, 0xe92f, 0x99c8, 0x89e9, 0xb98a, 0xa9ab,
        0x5844, 0x4865, 0x7806, 0x6827, 0x18c0, 0x08e1, 0x3882, 0x28a3,
        0xcb7d, 0xdb5c, 0xeb3f, 0xfb1e, 0x8bf9, 0x9bd8, 0xabbb, 0xbb9a,
        0x4a75, 0x5a54, 0x6a37, 0x7a16, 0x0af1, 0x1ad0, 0x2ab3, 0x3a92,
        0xfd2e, 0xed0f, 0xdd6c, 0xcd4d, 0xbdaa, 0xad8b, 0x9de8, 0x8dc9,
        0x7c26, 0x6c07, 0x5c64, 0x4c45, 0x3ca2, 0x2c83, 0x1ce0, 0x0cc1,
        0xef1f, 0xff3e, 0xcf5d, 0xdf7c, 0xaf9b, 0xbfba, 0x8fd9, 0x9ff8,
        0x6e17, 0x7e36, 0x4e55, 0x5e74, 0x2e93, 0x3eb2, 0x0ed1, 0x1ef0,
        ]

# base function for CRC  table
def _crc16(data, crc, table):
    
    # Calculate the checksum based on the passed in string
    # Each byte affects the checksum
    # How it works:
    # 1. Shift (and keep) last byte to the left
    # 2. XOR it with the table entry of the second to last byte XORed with the byte in the string
    # 3. Return the last 2 bytes
    for byte in data:
        crc = ((crc<<8)&0xff00) ^ table[((crc>>8)&0xff)^ord(byte)]
    return crc & 0xffff

# Calls the base function after the user passes in the data    
def crc16(data, crc=0):
    return _crc16(data, crc, CRC16_TABLE)

# Function to pipe a string into bits
# Used when sending data over   
def toBits(inputString):
    result = []
    for character in inputString:
        bits = bin(ord(character))[2:]
        bits = '00000000'[len(bits):] + bits
        result.extend([int(b) for b in bits])
    return result

def toString(inputBits):
    chars = []
    for bits in range(len(inputBits) / 8):
        byte = inputBits[bits*8:(bits+1)*8]
        chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
    return ''.join(chars)
    
    
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
        
        Button(master,text="Send File",command=self.send).grid(row=3,column=0)
        Button(master,text="Get File",command=self.get).grid(row=3,column=1)        

    def send(self):
        "Send a file" 
        #socket stuff
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(5)
        host = self.addr.get()
        port = int(self.port.get())
        #connect
        self.sock.connect((host, port))
        
        print "Checking if {} exists".format(self.fname.get())

        #Check to make sure the file actually exists
        check = os.path.isfile(self.fname.get())
        if check is True:
            # open the file
            file = open(self.fname.get(), "rb")
            print "{} opened".format(self.fname.get())
            # Counter is sent along with the packet so that the server knows which number packet it is
            counter = 1
            # Initiate the ACK packet to be blank
            ack_message = ""
            
            #keep sending the first packet until an ACK packet is received
            while (not ack_message):
                # Fill the first packet's header
                header = "new_" + self.fname.get() + " " + str(counter) + "_"
                # read enough data that there will be a total of 1024 bytes sent
                # (including header and checksum)

                data = file.read(packet_size - (len(toBits(header))/8) - 4)


                # Create a 2 byte checksum
                # Ends up being 4 bytes of the packet sent over
                # (1 byte per hex char)
                checksum = crc16(data)
                
                # ****** USED FOR TESTING *******
                #data = header + data
                #data_bits = toBits(data)
                #print len(data_bits)/8
                #print sys.getsizeof(data)
                #checksum_bits = str(format(checksum, '04X'))
                #print checksum_bits
                #test_checksum = toBits(str(checksum_bits))
                #print len(test_checksum)
                #print test_checksum
                #
                #data = header + data + str(format(checksum, '04X'))
                #data_bits = toBits(data)
                #
                #data = toString(data_bits)
                #print data
                #print len(data_bits)/8

               
                # Let the server know a new file is being sent along with the first packet
                self.sock.send(header + data + str(format(checksum, '04X')))
                sys.stdout.write('Sending...')
                ack_message = self.sock.recv(packet_size)
 
            # fill the second packet   
            counter = counter + 1
            header = self.fname.get()+" "+str(hex(counter))+"_"
            data = file.read(packet_size - (len(toBits(header))/8) - 4)
            ack_message = ""
            # Send the rest of the file over in packets
            
            while(data and not ack_message):
                # Empty the ack message at the beginning of sending each file
                # Sleep has been added in order to not over flow the buffer
                time.sleep(.15)
                checksum = crc16(data)

                # Send file's name and the next packet
                self.sock.send(header + data + str(format(checksum, '04X')))
                sys.stdout.write('.')
                ack_message = self.sock.recv(packet_size)
                # Get the next packet to be sent if the ack_message is all good
                if ack_message is not "":
                    # Update counter and header
                    counter = counter + 1
                    header = self.fname.get()+" "+str(counter)+"_"
                    data = file.read(packet_size - (len(toBits(header))/8) - 4)
                    ack_message = ""
                else:
                    print 'Packet {} was not received...resending'.format(counter)
                # If there is no more data, break out of the loop
                if data is 0:
                    break
            # Close file after sending
            file.close()
            print "Done!"

            print "Attempting to get a message back.."
            try:
                # Store returned message
                received = self.sock.recv(1024)
                # Print returned message
                print "Received: {}".format(received)
            except socket.timeout:
                print "Could not get a return message."
        else:
            print "{} does not exist...please try again".format(self.fname.get())
            
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
                    if received_checksum is crc16(data) and counter is packet_counter
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
