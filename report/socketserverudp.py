import socketserver
import datetime
class MyUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print("{} wrote:".format(self.client_address[0]))
        print(data)
        socket.sendto(data.upper(), self.client_address)




if __name__ == "__main__":

    HOST, PORT = "192.168.1.107", 6701
    server = socketserver.UDPServer((HOST, PORT), MyUDPHandler)
    server.serve_forever()



