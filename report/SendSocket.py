import socket



def sendSocket():
    HOST = '192.168.1.25'    # The remote host
    PORT = 6700               # The same port as used by the server
    # uid = r'20160102161538001=\\192.9.216.23\pacsimage2\NearLine\201603\20160316\X354954\A2614136'
    uid = r'20160102161538001.1=end'
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)   #socket.SOCK_DGRAM -for udp   socket.SOCK_STREAM- for tcp
    s.connect((HOST, PORT))
    s.sendall(bytes(uid,encoding='utf8',errors='字符串错误'))
    data = s.recv(1024)
    s.close()
    print('Received', repr(data))

if __name__ == '__main__':
   sendSocket()