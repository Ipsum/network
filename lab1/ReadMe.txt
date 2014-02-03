---- ReadMe.txt for UDP server and client ---
 - Authors: David Tyler and Andrew Hajj
 - Date:    2/2/14
 - Modules: Server.py, Client.py
 
 Client.py:
 
 Client.py is the module run as the UDP client process.
    - To run Client.py, first make sure that the server on cato.ednos.net is up.
    - To change the host or port, edit HOST or PORT in Client.py 
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
    