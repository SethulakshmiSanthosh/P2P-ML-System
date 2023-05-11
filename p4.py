'''import socket
import threading

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.receive_thread = threading.Thread(target=self.receive_data)
        self.receive_thread.start()

    def send_data(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def receive_data(self):
        while True:
            data = self.socket.recv(1024)
            if not data:
                break
            print(f"Received data: {data.decode('utf-8')}")

    def start(self):
        while True:
            data = input("Enter data to send: ")
            self.send_data(data)

if __name__ == '__main__':
    peer = Peer("127.0.0.1", 8001)
    peer.start()
'''
import socket
import threading

class Peer:
    def __init__(self, host, port, peers):
        self.host = host
        self.port = port
        self.peers = peers
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(1)
        self.connected_peers = []
        self.receive_thread = threading.Thread(target=self.receive_data)
        self.receive_thread.start()

        self.data_lock = threading.Lock()
        self.global_data = "init data"

    def connect_to_peers(self):
        for peer in self.peers:
            if peer != (self.host, self.port):
                peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    peer_socket.connect(peer)
                    self.connected_peers.append(peer_socket)
                    print(f"Connected to peer: {peer}")
                except ConnectionRefusedError:
                    print(f"Connection to peer {peer} refused")
                    self.connect_to_peers()

    def send_data(self, data):
        for peer in self.connected_peers:
            peer.sendall(data.encode('utf-8'))

    def receive_data(self):
        while True:
            conn, addr = self.socket.accept()
            print(f"Connected by {addr}")
            self.connected_peers.append(conn)
            threading.Thread(target=self.handle_connection, args=(conn,)).start()

    def handle_connection(self, conn):
        while True:
            data = conn.recv(1024)
            if not data:
                self.connected_peers.remove(conn)
                conn.close()
                break
            # self.update_global_data(data.decode('utf-8'))
            self.update_global_data(data)
            print("Received data from a peer")
            # data = input("Enter data to send: ")
            # # self.update_global_data(data.decode('utf-8'))
            # self.update_global_data(data)
            # self.send_data(data)

    def update_global_data(self, new_data):
        with self.data_lock:
            self.global_data = new_data
            print(f"Global data updated: {self.global_data}")

    def start(self):
        self.connect_to_peers()
        while True:
            data = input("Enter data to send: ")
            self.update_global_data(data.encode('utf-8'))
            self.send_data(data)
        
# Peer 4
if __name__ == '__main__':
    peers = [("127.0.0.1", 8001), ("127.0.0.1", 8002), ("127.0.0.1", 8003)]
    peer4 = Peer("127.0.0.1", 8004, peers)
    threading.Thread(target=peer4.start).start()
