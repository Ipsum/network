---- ReadMe.txt for UDP server and client ---
 - Authors: David Tyler and Andrew Hajj
 - Date:    3/16/14
 - Modules: Server.py, Client.py
 
 Required:
    - Python 2.7.x
    - Windows or Linux

 server.py:
 
 This module provides a simple udp server for receiving and sending files
    - To run this module, have python 2.7 installed and use the syntax:
               python server.py [ip] [port]
        where the ip and port are the ip and port to serve on.
    - localhost can be used as the ip for ease of testing
    - any files that the server receives will be in the same directory
        as the scipt


 Client.py:
 
 Client.py is the module run as the UDP client process.
    - do python client.py
    - enter the address of the server eg: cato.ednos.net or localhost
    - enter the port of the server eq: 4422 or 9999
    - enter the file name: sample.jpg
    - press send file to send a file of the entered name in the same directory as the script
    - Option 1 is default (no intentional corruption)
    - Option 2 can be selected to intentionally corrupt data in ACK on the sender side
    - Option 3 can be selected to intentionally corrupt data in the packet on the receiver side
    - press get file to get the entered file from the server
