---- ReadMe.txt for UDP server and client ---
 - Authors: David Tyler and Andrew Hajj
 - Date:    4/22/14
 - Modules: Sender.py, Receiver.py
 
 Required:
    - Python 2.7.x
    - Windows or Linux

 receiver.py:
 
 This module provides a TCP server for receiving and sending files
    - To run this module, have python 2.7 installed and use the syntax:
               python receiver.py [ip] [port] [opt3] [opt5]
        where the ip and port are the ip and port to serve on,
	and Y or N is inputed for opt3 and opt5.
	if Y is inputted for opt3, receiver.py will intentionally corrupt data in the header on the receiver side,
	if Y is inputted for opt5, receiver.py will intentionally drop a received data packet in the header on the receiver side
    - localhost can be used as the ip for ease of testing
    - any files that the server receives will be in the same directory
        as the scipt


 sender.py:
 
 sender.py is the module run as the TCP sending process.
     - To run this module, have python 2.7 installed and use the syntax:
               python sender.py [ip] [port] [opt2] [opt4]
        where the ip and port are the ip and port to serve on,
	and Y or N is inputed for opt2 and opt4.
	if Y is inputted for opt2, receiver.py will intentionally corrupt data in ACK on the sender side,
	if Y is inputted for opt4, receiver.py will intentionally drop the received ACK packet at the sender
    - the file to be sent can be changed by changing '_FILENAME' in sender.py
    - ensure that the file to be sent is in the directory as sender.py
    - localhost can be used as the ip for ease of testing

