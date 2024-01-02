import socket
import threading
from _thread import *
from utils import *
import json


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

player_count = 0
connections = {}
sync_lock = threading.Lock()


def threaded_client(conn, player_id, sync_lock):
    global player_count
    print(f"Player {player_id} connected from {conn}")
    # Envoi de l'ID
    conn.send(str(player_id).encode())

    with sync_lock:
        connections[player_id] = conn

    while True:
        try:
            with sync_lock:
                data = conn.recv(2048*2).decode()
            reply = {}
            if not data:
                print(f"Connection with player {player_id} closed.")
                break
            else:
                reply = json.loads(data)
                # Traiter les modifs
                print(f"Received: {reply}")
                with sync_lock:
                    if "position" in reply:
                        if reply["player_id"] == 1:
                            if 2 in connections:
                                connections[2].send(json.dumps(reply).encode("utf-8"))
                        elif reply["player_id"] == 2:
                            if 1 in connections:
                                connections[1].send(json.dumps(reply).encode("utf-8"))
                    elif "started" in reply:
                        if reply["player_id"] == 1:
                            if 2 in connections:
                                connections[2].send(json.dumps(reply).encode("utf-8"))
                        elif reply["player_id"] == 2:
                            if 1 in connections:
                                connections[1].send(json.dumps(reply).encode("utf-8"))
                    elif "ball" in reply:
                        if reply["player_id"] == 1:
                            if 2 in connections:
                                connections[2].send(json.dumps(reply).encode("utf-8"))
                        elif reply["player_id"] == 2:
                            if 1 in connections:
                                connections[1].send(json.dumps(reply).encode("utf-8"))

        except Exception as e:
            print(f"Error {player_id}: {e}")
            break

    with sync_lock:
        del connections[player_id]
    print("Connection Closed")
    conn.close()


while True:
    conn, addr = s.accept()
    player_count += 1
    print(f"Connected to: {addr}")
    start_new_thread(threaded_client, (conn, player_count, sync_lock))
