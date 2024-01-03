import socket
import time
from _thread import *
from utils import *
import json
from queue import Queue


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((host_server, port_server))
except socket.error as e:
    print(str(e))

s.listen(2)
print("Waiting for a connection")

player_count = 0
connections = {}
shared_queue = Queue()


def threaded_client(conn, player_id):
    global player_count
    print(f"Player {player_id} connected from {conn}")
    # Envoi de l'ID
    conn.send(str(player_id).encode())

    connections[player_id] = conn
    print(connections)

    # Attend que le client soit prêt
    ready_signal = conn.recv(1024).decode('utf-8')
    if ready_signal == "READY":
        # Mettez un message dans la queue pour indiquer que le client est prêt
        shared_queue.put(f"READY_{player_id}")
        print(shared_queue.queue)

    while not (shared_queue.qsize() == 2 and "READY_1" in shared_queue.queue and "READY_2" in shared_queue.queue):
        pass

    # Envoyez un signal au client pour indiquer que les deux joueurs sont prêts
    conn.send("START".encode('utf-8'))

    while True:
        reply = {}
        try:
            data = conn.recv(2048*2).decode()
            if not data:
                print(f"Connection with player {player_id} closed.")
                break
            else:
                reply = json.loads(data)
                # Traiter les modifs
                print(f"Received: {reply}")
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

    del connections[player_id]
    print("Connection Closed")
    conn.close()


while True:
    conn, addr = s.accept()

    player_count += 1
    print(f"Connected to: {addr}")

    start_new_thread(threaded_client, (conn, player_count))
