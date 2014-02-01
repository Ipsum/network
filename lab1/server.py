#!/usr/bin/env python

""" server.py

 A simple UDP server to receive and send files over the internet

 Usage:
  Run this file with arguments for the ip and socket to bind to.
  
  python server.py cato.ednos.net 4422


 Files are saved and served from same directory as this script.
 Files are sent and received in the format: filename binaryfiledata
 Example test.txt:
  test.txt this is a test file

"""

import SocketServer
import sys

__author__ = "David Tyler"
__credits__ = ["Andrew Hajj","David Tyler"]
__license__ = "MIT"
__email__ = "dtyler@gmail.com"
__status__ = "Development"

# only change these if not run with commandline args
_HOST_ = "cato.ednos.net"
_PORT_ = 4422

class MyUDPHandler(SocketServer.BaseRequestHandler):
    "UDP server class to handle incoming data and return response"

    def handle(self):
        """Handle incoming UDP data - decide if file or command
        Commands: list (lists files), 
                  filename (responds with contents of [filename])
        Other data assumed to be a file to save
        """    
        
        data = self.request[0].strip()
        socket = self.request[1]
        if data=="list":
            #return list of files in directory
            pass
        #split off first word of file, assume is filename
        filename,sep,data = data.partition(" ")
        if not data:
            #assume is requesting file
            try:
                f = open(filename,'rb')
            except:
                socket.sendto("{} not found".format(filename),
                 self.client_address)
                print "can't find "+filename
                return False
            # suceeded in opening file, now send
            output = filename+" "+f.read()
            socket.sendto(output,self.client_address)
            f.close()
            return True
        else:
            #assume we have to save the file
            try:
                f = open(filename,'w')
            except:
                socket.sendto("problem saving file!",self.client_address)
                return False
            f.write(data)
            f.close()
            print "written"
            socket.sendto("{} saved!".format(filename),self.client_address)
            return True
        print "Never be here"

if __name__ == "__main__":
    try:
        HOST, PORT = sys.argv[1],int(sys.argv[2])
    except:
        HOST, PORT = _HOST_,int(_PORT_)
    print HOST+str(PORT)
    server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    server.serve_forever()
