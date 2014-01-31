import SocketServer

class MyUDPHandler(SocketServer.BaseRequestHandler):
    "UDP server class to handle incoming data and return response"

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print "{} wrote:".format(self.client_address[0])
        print data
        socket.sendto(data.upper(), self.client_address)

if __name__ == "__main__":
    HOST, PORT = "cato.ednos.net", 4422
    server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    server.serve_forever()
