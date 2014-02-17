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
#
# ******** UPDATED 2/13/14 ***********

# Now splits the file in to 1kb packets to be sent over to the server
# Size of the packets can be changed by modifying the buffer

import socket
import sys
import time
import os

#HOST, PORT = "cato.ednos.net", 4422
HOST, PORT = "localhost", 9999

# Size of the packets to be sent
buf = 1024

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect((HOST, PORT))
sock.settimeout(20)

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

    print "Checking if {} exists".format(fileName)

    #Check to make sure the file actually exists
    check = os.path.isfile(fileName)
    if check is True:
        # open the file
        file = open(fileName, "rb")
        print "{} opened".format(fileName)
        # Counter is sent along with the packet so that the server knows which number packet it is
        counter = 1
        # Fill the first packet
        data = file.read(buf)
        # Let the server know a new file is being sent along with the first packet
        sock.send("new_" + fileName + " " + str(counter) + "_" + data)
        sys.stdout.write('Sending...')
        data = file.read(buf)
        # Send the rest of the file over in packets
        while(data):
            # Sleep has been added in order to not over flow the buffer
            time.sleep(.15)
            counter = counter + 1
            # Send file's name and the next packet
            sock.send(fileName+" "+str(counter)+"_"+data)
            sys.stdout.write('.')
            # Get the next packet to be sent
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
            received = sock.recv(1024)
            # Print returned message
            print "Received: {}".format(received)
        except socket.timeout:
            print "Could not get a return message."
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

    print "Creating {} from server...".format(sock.recv(buf))
    
    # Now get and write the data (in 1kb packets)
    data = sock.recv(buf + sys.getsizeof(fileName+" "))
    sys.stdout.write('Receiving...')
    try:
        while(data):
            #Parse the packet
            recievedFileName, sep, data = data.partition(" ")
            sys.stdout.write('.')
            # Write that packet to the file
            file.write(data)
            #Receive the next packet to be saved to the file
            data = sock.recv(buf + sys.getsizeof(fileName+" "))
    except socket.timeout:
        print "Done!"
        print "***    Received file: {}   ***".format(recievedFileName)

    file.close()

else:
    print "Requested action, {}, is not recognised...".format(action)
    print "Supported actions are: send [s or send] or get [g or get]"


# Close socket connection
sock.close()
