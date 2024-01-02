import socket
import threading
import json

from utils import *


class PongServer:
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(2)
        self.players = {}
        self.nex_player_id = 1
        self.players_ready = 0
        self.lock = threading.Lock()

        # DATA
        self.ball_x = width / 2
        self.ball_y = height / 2
        self.paddle_A_y = top_A
        self.paddle_B_y = top_B
        self.started = False

    def accept_connections(self):
        while True:
            player_socket, addr = self.socket.accept()
            player_id = self.nex_player_id
            self.nex_player_id += 1

            self.players[player_id] = player_socket
            print(f"Player {player_id} connected from {addr}")

            # Envoi de l'ID au client
            player_socket.send(str(player_id).encode("utf-8"))

            with self.lock:
                self.players_ready += 1
                if self.players_ready == 2:
                    self.broadcast({"message": "start_game"})
                    self.players_ready = 0

    def handle_player(self, player_id):
        player_socket = self.players[player_id]

        while True:
            try:
                data = player_socket.recv(1024).decode("utf-8")
                print("ici7")
                if not data:
                    print(f"Connection with player {player_id} closed.")
                    del self.players[player_id]
                    break
                else:
                    data = json.loads(data)
                    # TRAITER LES MODIFS
                    print(f"Received: {data}")
                    if "position" in data:
                        print("position")
                        if data["player_id"] == 1:
                            self.paddle_A_y = data["position"]["paddle_y"]
                            self.broadcast(data, 2)
                        elif data["player_id"] == 2:
                            self.paddle_B_y = data["position"]["paddle_y"]
                            self.broadcast(data, 1)
                    elif "started" in data:
                        print("started")
                        if data["player_id"] == 1:
                            self.started = data["started"]
                            self.broadcast(data, 2)
                        elif data["player_id"] == 2:
                            self.started = data["started"]
                            self.broadcast(data, 1)
            except Exception as e:
                print(f"Error handling player {player_id}: {e}")
                break

    def broadcast(self, data, player_id=None):
        with self.lock:
            players_to_remove = []

            if player_id is not None:
                player_socket = self.players.get(player_id)
                if player_socket:
                    try:
                        player_socket.send(json.dumps(data).encode("utf-8"))
                    except Exception as e:
                        print(f"Error broadcasting to player {player_id}: {e}")
                        del self.players[player_id]
            else:
                for player_id, player_socket in self.players.items():
                    try:
                        player_socket.send(json.dumps(data).encode("utf-8"))
                    except Exception as e:
                        print(f"Error broadcasting to player {player_id}: {e}")
                        del self.players[player_id]

        # for player_id in players_to_remove:
        #     del self.players[player_id]

    def game_loop(self):
        while True:
            game_data = {
                "players": {
                    1: {"ball_x": self.ball_x, "ball_y": self.ball_y, "paddle_y": self.paddle_A_y, "started": self.started},
                    2: {"ball_x": self.ball_x, "ball_y": self.ball_y, "paddle_y": self.paddle_B_y, "started": self.started}
                }
            }

            # self.broadcast(game_data)

    def start(self):
        accept_thread = threading.Thread(target=self.accept_connections)
        accept_thread.start()

        handle_threads = [threading.Thread(target=self.handle_player, args=(player_id,)) for player_id in self.players.keys()]
        for thread in handle_threads:
            thread.start()

        # game_thread = threading.Thread(target=self.game_loop)
        # game_thread.start()


if __name__ == '__main__':
    server = PongServer(host_server, port_server)
    server.start()
