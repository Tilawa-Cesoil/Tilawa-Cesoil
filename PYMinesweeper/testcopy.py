import socket
port=31259
password='PYMinesweeper by Tilawa Cesoil'.encode('utf-8')
internet=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# internet.bind(('127.0.0.1',port))
# internet.listen(1)
def connect(host:str):
    internet.connect((host,port))
    internet.send(password)
connect('127.0.0.1')
# conn,address=internet.accept()
# message=internet.recv(1024)
# print(message.decode('utf-8'))