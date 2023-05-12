import socket
import threading
import pickle
from sklearn.ensemble import VotingClassifier

class Peer:
    def __init__(self, host, port, peers):
        self.host = host
        self.port = port
        self.peers = peers
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(1)
        self.connected_peers = []
        self.receive_thread = threading.Thread(target=self.receive_model)
        self.receive_thread.start()

        self.model_lock = threading.Lock()
        self.global_model = None

    def connect_to_peers(self):
        for peer in self.peers:
            if peer != (self.host, self.port):
                peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    peer_socket.connect(peer)
                    self.connected_peers.append(peer_socket)
                    print(f"Connected to peer: {peer}")
                except ConnectionRefusedError:
                    self.connect_to_peers()

    def send_model(self, model):
        serialized_model = pickle.dumps(model)
        for peer in self.connected_peers:
            peer.sendall(serialized_model)

    def receive_model(self):
        while True:
            conn, addr = self.socket.accept()
            self.connected_peers.append(conn)
            threading.Thread(target=self.handle_connection, args=(conn,)).start()

    def handle_connection(self, conn):
        while True:
            serialized_model = conn.recv(5024)  # Adjust buffer size as per your requirement
            if not serialized_model:
                self.connected_peers.remove(conn)
                conn.close()
                break
            received_model = pickle.loads(serialized_model)
            self.update_global_model(received_model)
            print("Received model from a peer")

    def update_global_model(self, received_model):
        with self.model_lock:
            if self.global_model is None:
                self.global_model = received_model
            else:
                self.global_model = VotingClassifier(estimators=[('self.global_model', self.global_model), ('recieved_model', self.receive_model)], voting='hard')
                # self.global_model = (self.global_model + received_model) / 2
            print("Global model updated")

    def start(self):
        self.connect_to_peers()
        t=5
        while (t>0):
            import pandas as pd
            import numpy as np
            import os
            from sklearn.naive_bayes import GaussianNB
            from sklearn.model_selection import train_test_split
            Data = pd.read_csv("./wine_dataset_p1.csv")
            Data["style"] = np.where(Data["style"] == "white", 1, 0)
            # feature - target
            x = Data.drop(["style"], axis = 1)
            y = Data["style"]
            # train - test
            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.33, random_state = 45)
            Model = GaussianNB()
            Model.fit(x_train, y_train)
            local_model = Model
            self.update_global_model(local_model)
            self.send_model(local_model)
            t=t-1
        
# Peer 1
if __name__ == '__main__':
    peers = [("10.113.17.122", 8001), ("10.113.6.132", 8002), ("10.113.17.139", 8003)]
    # peers = [("127.0.0.1", 8002)]
    peer4 = Peer("10.113.17.73", 8004, peers)
    threading.Thread(target=peer4.start).start()