# -------- C l i e n t . p y -------- #
# Author: Andrew Hajj
# Date: 2/1/14
# Source: Code borrowed and modified from "http://docs.python.org/2/library/socketserver.html"
# Purpose: Client side for a UDP server in Python.

import socket
import sys

HOST, PORT = "cato.ednos.net", 4422
data = " ".join(sys.argv[1:])

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Data is sent to the host using the function sendto().
sock.sendto(data + "\n", (HOST, PORT))
received = sock.recv(1024)

print "Sent:     {}".format(data)
print "Received: {}".format(received)