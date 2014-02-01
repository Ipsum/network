# -------- C l i e n t . p y -------- #
# Author: Andrew Hajj
# Date: 2/1/14
# Source: Code borrowed and modified from "http://docs.python.org/2/library/socketserver.html"
# Purpose: Client side for a UDP server in Python.

import socket
import sys
import os

HOST, PORT = "cato.ednos.net", 4423

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((HOST, PORT))

# Get the name of the file to be sent
fileName = sys.argv[1]

# Print the name of the file locally (to ensure it is correct)
print fileName

# Open the file
file = open(fileName, "rb")

# Collect file's data and size
data = file.read()

# Begin sending over the file's information (name and data)
#sock.send(fileName) # Send file name
#sock.send(str(size)) # Send size of file
sock.send(fileName+" "+data) # Send file's data

# Close file after sending
file.close()

# Store returned message
received = sock.recv(1024)

# Close socket connection
sock.close()

# Print returned message
print "Received: {}".format(received)
