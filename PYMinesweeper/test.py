import socket,threading
port=31259
password='PYMinesweeper by Tilawa Cesoil'.encode('utf-8')
def connect(host):
    client.connect((host,port))
    client.send(password)
server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(('127.0.0.1',port))
server.listen(1)
def receive():
    while True:
        conn,address=server.accept()
        message=conn.recv(1024)
        if not message.decode('utf-8')==password:conn.close()
threading.Thread(target=receive,daemon=True).start()
while True:
    a=input()
    if a=='q':break
    else:
        connect('127.0.0.1')