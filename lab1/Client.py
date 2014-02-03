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
# Usage:    Run this file with arguments to send/get a file to/from the server
#           ex. 'python Client.py send sample.jpg'

import socket
import sys
import os

HOST, PORT = "cato.ednos.net", 4423

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((HOST, PORT))

# When running the file, it should be run as 'Client.py action fileName'
# ex. Client.py send image.jpg

# Get info on send or receive
action = sys.argv[1]

# Get the name of the file
fileName = sys.argv[2]

# Print the action and name of the file locally (to ensure it is correct)
print "You chose to", action, fileName

# Sending an image
if action.lower() in ["s", "send"]:

    # Let the server know we are sending a file over
    #sock.send(putting)

    print "Checking if {} exists".format(fileName)
    # Open the file

    #Check to make sure the file actually exists
    check = os.path.isfile(fileName)
    if check is True:
        file = open(fileName, "rb")
        print "{} opened".format(fileName)

        data = file.read()

        # Begin sending over the file's information (name and data)
        # Keep file under 10 kB for best results

        # Send file's name and data
        sock.send(fileName+" "+data)

        # Close file after sending
        file.close()

        # Store returned message
        received = sock.recv(1024)

        # Print returned message
        print "Received: {}".format(received)
    else:
        print "{} does not exist...please try again".format(fileName)


elif action.lower() in ["g", "get"]:

    print "Requesting", fileName+"..."

    # Create a new file
    try:
        file = open(fileName, 'wb')
    except:
        print "There was a problem saving the file..."

    # Send the name of the file to be pulled from the server
    sock.send(fileName)

    # Now get and write the data (up to 10 kB)
    data = sock.recv(10240)

    recievedFileName, sep, data = data.partition(" ")
    print "***    Received file: {}   ***".format(recievedFileName)

    file.write(data)
    file.close()

else:
    print "Requested action, {}, is not recognised...".format(action)
    print "Supported actions are: send [s or send] or get [g or get]"


# Close socket connection
sock.close()
