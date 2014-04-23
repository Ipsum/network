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
               python receiver.py [ip] [port] [option 3 (% chance of corruption)] [option 5 (% chance of packet loss)]
        where the ip and port are the ip and port to serve on,
	and the percentages that are inputed for option 3 and option 5.
	if a value is inputted for opt3, there is a that-value percent chance that receiver.py will intentionally corrupt data in the header on the receiver side,
	if a value is inputted for opt5, there is a that-value percent chance that receiver.py will intentionally drop a received data packet in the header on the receiver side
    - localhost can be used as the ip for ease of testing
    - any files that the server receives will be in the same directory
        as the scipt


 sender.py:
 
 sender.py is the module run as the TCP sending process.
     - To run this module, have python 2.7 installed and use the syntax:
               python sender.py [ip] [port] [option 2 (% chance of corruption)] [option 4 (% chance of packet loss)]
        where the ip and port are the ip and port to serve on,
	and the percentages that are inputed for opt2 and opt4.
	if a value is inputted for opt2, there is a that-value percent chance that receiver.py will intentionally corrupt data in ACK on the sender side,
	if a value is inputted for opt4, there is a that-value percent chance that receiver.py will intentionally drop the received ACK packet at the sender
    - the file to be sent can be changed by changing '_FILENAME' in sender.py
    - ensure that the file to be sent is in the directory as sender.py
    - localhost can be used as the ip for ease of testing

