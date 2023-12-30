import socket
from _thread import *
from utils import *

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = 'localhost'
port = port_server

server_ip = socket.gethostbyname(server)


try:
    s.bind((host_server, port))
except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection")

currentId = "0"
pos_paddle = [f"0:{left_A},{top_A}", f"1:{left_B},{top_B}"]
# pos_ball = [f"0:{width/2},{height/2}", f"1:{width/2},{height/2}"]


def threaded_client(conn):
    global currentId, pos_paddle#, pos_ball
    conn.send(str.encode(currentId))
    currentId = "1"
    reply = ''
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode('utf-8')
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                print("Received: " + reply)
                arr = reply.split(":")
                id = int(arr[0])
                pos_paddle[id] = reply
                # pos_ball[id] = reply

                if id == 0: nid = 1
                if id == 1: nid = 0

                reply = pos_paddle[nid][:]
                print("Sending: " + reply)

            conn.sendall(str.encode(reply))
        except:
            break

    print("Connection Closed")
    conn.close()


while True:
    conn, addr = s.accept()
    print(f"Connected to: {addr}")

    start_new_thread(threaded_client, (conn,))
