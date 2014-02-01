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

# When running the file, it should be run as 'Client.py action fileName'
# ex. Client.py send image.jpg 
# Get info on send or receive
action = " ".join(sys.argv[1])

# Get the name of the file
fileName = " ".join(sys.argv[2])

# Print the action and name of the file locally (to ensure it is correct)
print action, fileName

# Sending an image
if action.lower in [s, send]:

    # Let the server know we are sending a file over
    #sock.send(putting)

    # Open the file
    file = open(fileName, "rb")

    # Begin sending over the file's information (name and data)
    sock.send(fileName+" "+data) # Send file's data
    
    # Close file after sending
    file.close()

    # Store returned message
    received = sock.recv(1024)
    
    # Print returned message
    print "Received: {}".format(received)

elif action.lower in [g, get]:    

    # Let the server know we are pulling a file
    #sock.send(getting)
    
    # Create a new file 
    try:
        file = open(fileName, 'w')
    except:
        print "Problem saving file!"
        
    # Send the name of the file to be pulled from the server
    sock.send(fileName)
    
    # Now get and write the data
    data = sock.recv(1024)
    while (data):
        file.write(data)
        data = sock.recv(1024)
    file.close
    
    # Send confirmation message
    sock.send("Successfully received file!")
    
    # Print returned message
    print "Received: {}".format(received)


# Close socket connection
sock.close()

