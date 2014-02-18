---- ReadMe.txt for UDP server and client ---
 - Authors: David Tyler and Andrew Hajj
 - Date:    2/2/14
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
    - any files that the server sends or receives will be in the same directory
        as the scipt


 Client.py:
 
 Client.py is the module run as the UDP client process.
    - To run Client.py, first make sure that the server on cato.ednos.net is up.
    - To change the host or port, edit HOST or PORT in Client.py 
    - NOTE - best results when files are under 10kb
    - To send a file to the server:
        1. First add the desired file to the folder containing Client.py
        2. Run the Command prompt (on Windows)
        3. Navigate to the directory containing the file and Client.py
        4. Run the script in the following manner - "python Client.py send -filename-"
            - Alternatively, 's' can be used instead of 'send'
    - To get a file from the server:
        1. First add the desired file to the folder containing Client.py
        2. Run the Command prompt (if in Windows)
        3. Navigate to the directory containing the file and Client.py 
        4. Run the script in the following manner - "python Client.py get -filename-"
            - Alternatively, 'g' can be used instead of 'g'
        5. The file should then be available in the directory
    
2_ - To send a file to the server:
        1. First add the desired file to the folder containing Client.py
        2. Run the Command prompt (on Windows)
        3. Navigate to the directory containing the file and Client.py
        4. Run the script in the following manner - "python Client.py send -filename-"
            - Alternatively, 's' can be used instead of 'send'
    - To get a file from the server:
        1. First add the desired file to the folder containing Client.py
        2. Run the Command prompt (if in Windows)
        3. Navigate to the directory containing the file and Client.py 
        4. Run the script in the following manner - "python Client.py get -filename-"
            - Alternatively, 'g' can be used instead of 'g'
        5. The file should then be available in the directory