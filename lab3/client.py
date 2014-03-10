# -------- C l i e n t . p y -------- #
# Author: Andrew Hajj
# Email: andrew.hajj@gmail.com
# Credits: David Tyler, Andrew Hajj
# Date: 2/1/14
# Source:   Code was built off of
#           "http://docs.python.org/2/library/socketserver.html",
#           but holds little similarity now
# Purpose: Client side for a UDP server in Python.  Can send and receive files
#          (under 10kB works best, as found from tests)
# Usage:    Run this file and use gui to specify file to send/receive and the server details
#           ex. 'python client.py'
#
# ******** UPDATED 3/09/14 ***********
#

# ******** UPDATED 2/13/14 ***********
# Now splits the file in to 1kb packets to be sent over to the server
# Size of the packets can be changed by modifying the buffer

import socket
import sys
import time
import os

from Tkinter import *
from ttk import *

#HOST, PORT = "cato.ednos.net", 4422
HOST, PORT = "localhost", 9999

# Size of the packets to be sent
buf = 1024

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
                # Fill the first packet
                data = file.read(buf)
                # Let the server know a new file is being sent along with the first packet
                self.sock.send("new_" + self.fname.get() + " " + str(counter) + "_" + data)
                sys.stdout.write('Sending...')
                ack_message = self.sock.recv(buf)
                # Check for the case were ack_message is filled incorrect
                if ack_message is not "Packet Received"
                    ack_message = ""
                    
            data = file.read(buf)
            # Send the rest of the file over in packets
            while(data and not ack_message):
                ack_message = ""
                # Sleep has been added in order to not over flow the buffer
                time.sleep(.15)
                counter = counter + 1
                # Send file's name and the next packet
                self.sock.send(self.fname.get()+" "+str(counter)+"_"+data)
                sys.stdout.write('.')
                ack_message = self.sock.recv(buf)
                # Get the next packet to be sent if the ack_message is all good
                if ack_message is not ""
                    data = file.read(buf)
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

        return_message = self.sock.recv(buf)
        #print return_message
        if "not found" in return_message:
            print "{} not found".format(self.fname.get())
        else:
            print "Creating {} from server...".format(return_message)
        
            # Now get and write the data (in 1kb packets)
            data = self.sock.recv(buf + sys.getsizeof(self.fname.get()+" "))
            sys.stdout.write('Receiving...')
            try:
                while(data):
                    #Parse the packet
                    recievedFileName, sep, data = data.partition(" ")
                    sys.stdout.write('.')
                    # Write that packet to the file
                    file.write(data)
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
