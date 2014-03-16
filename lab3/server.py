#!/usr/bin/env python

""" server.py

 A simple UDP server to receive and send files over the internet

 Usage:
  Run this file with arguments for the ip and self.socket to bind to.

  python server.py cato.ednos.net 4422


 Files are saved and served from same directory as this script.
 Files are sent and received in the format: filename binaryfiledata
 Example test.txt:
  test.txt this is a test file

"""

import SocketServer
import sys
import time
import struct

__author__ = "David Tyler"
__credits__ = ["Andrew Hajj", "David Tyler"]
__license__ = "MIT"
__email__ = "dtyler@gmail.com"
__status__ = "Development"
# only change these if not run with commandline args
_HOST = "localhost"
#_HOST = "cato.ednos.net"
_PORT = 9999
#_PORT = 4422
PKTNUMBR = 0

class MyUDPHandler(SocketServer.BaseRequestHandler):
    "UDP server class to handle incoming data and return response"

    def handle(self):
        """Handle incoming UDP data - decide if file or command
        Commands: list (lists files),
                  filename (responds with contents of [filename])
        Other data assumed to be a file to save
        """

        # Only strip the white space on the left as there could be
        # trailing white space in the data that is needed
        data = self.request[0].lstrip()
        self.socket = self.request[1]

        #split off first word of file, assume is filename
        data = struct.unpack("!?125cH")

        if crc16(struct.pack("!?125c",*data[:-1]) != data[-1]:
            self.ack(not PKTNUMBR)
        if "".join(data[0:4])=="new_":
            self.data=

        #assume is requesting file
        if not data:
            self.sendfile(filename)
        #assume we have to save the  file since data was sent
        # New file was specified
        elif "new_" in filename:

            # Counter is used to display the packet number sent
            counter, sep, data = data.partition("_")
            new, sep, filename = filename.partition("_")
            checksum = data[-4:]
            if self.check(data[:-4],checksum):
                print "Recieved packet {} of {}".format(counter, filename)
                self.createfile(filename, data)
            print data.encode('hex')
        # If not specified to create a new file, add on to existing
        else:
            # Again, counter is used to display the packet number sent
            counter, sep, data = data.partition("_")
            checksum = data[-4:]
            if self.check(data[:-4],checksum):
                print "Recieved packet {} of {}".format(counter, filename)
                self.savefile(filename, data)
            print data.encode('hex')
        return True
        
    def check(self,data,checksum):
        if(self.crc16(data)==checksum):
            return True
        return False
        
    def swap_bytes(self,word_val):
        """swap lsb and msb of a word"""
        msb = word_val >> 8
        lsb = word_val % 256
        return (lsb << 8) + msb   
    
    def crc16(self,data):
        """Calculate the CRC16 of a datagram"""
        crc = 0xFFFF
        for i in data:
            crc = crc ^ ord(i)        
            for j in xrange(8):
                tmp = crc & 1
                crc = crc >> 1
                if tmp:
                    crc = crc ^ 0xA001
        return self.swap_bytes(crc)    
    
    def createfile(self, filename, data):
        "Overwrite existing file if we get a file by the same name"
        # Used for the first packet of a file.
        # Creates a new file of the specified name
        try:
            f = open(filename, 'wb')
            f.write(data)
        except:
            self.socket.sendto("could not erase old file", self.client_address)
        f.close()
        return True

    def savefile(self, filename, data):
        "Save file that was sent to this server via UDP self.socket"
        # Appends the data to the end of the file.
        # Used for the second packet on for a file
        try:
            f = open(filename, 'ab')
        except:
            self.socket.sendto("problem saving file!", self.client_address)
            return False
        f.write(data)
        f.close()

        self.socket.sendto("{} saved!".format(filename), self.client_address)

        return True


    def sendfile(self, filename):
        "This function responds to client with requested file"

        try:
            f = open(filename, 'rb')
        except:
            self.socket.sendto("{} not found".format(filename),
            self.client_address)
            print "can't find "+filename
            return False

        #succeeded in opening file, now send requested file to client 1kb
        #chunks first indicate the start of a file with: "new filename"
        self.socket.sendto("new "+filename, self.client_address)
        #spool out the data kb by kb
        data = f.read(1024)
        while data:
            # wait before sending the next instruction in order to not
            # overflow the buffer
            time.sleep(.15)
            output = filename+" "+data
            # Send the parsed data
            self.socket.sendto(output, self.client_address)
            # Read in the next packet to be sent
            data = f.read(1024)
        f.close()

        return True


if __name__ == "__main__":
    try:
        HOST, PORT = sys.argv[1], int(sys.argv[2])
    except:
        HOST, PORT = _HOST, int(_PORT)

    print "Running on "+HOST+":"+str(PORT)
    server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    server.serve_forever()
