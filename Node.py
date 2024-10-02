import socket
import threading
import json
import time

class P2PNode:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = {}  # Stores IP addresses and ports of other peers
        self.lock = threading.Lock()  # For safe editing of the peer list
        self.is_running = True

        # Run the server
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.start()

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        print(f"Server started on port {self.host}:{self.port}")

        while self.is_running:
            try:
                client_socket, addr = server_socket.accept()
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            except Exception as e:
                print(f"Server encountered an error: {e}")
                break

    def handle_client(self, client_socket):
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                return

            message = json.loads(data)

            if message['type'] == 'JOIN': # New node wants to join the network
                # Update own peers list and return the list of known peers
                response = json.dumps({'type': 'PEERS', 'peers': self.peers})
                with self.lock:
                    self.peers[message['host']] = message['port']
                client_socket.send(response.encode('utf-8'))
                print(f"New peer added to the list: {message['host']}:{message['port']}")

                # Broadcast the new peer to the other peers
                self.broadcast_new_peer(message['host'], message['port'])

            elif message['type'] == 'LEAVE':
                # Peer leaves the network
                self.remove_peer(message['host'], message['port'])

            elif message['type'] == 'NEW_PEER':
                # New peer joined the network, update the list of peers
                with self.lock:
                    self.peers[message['host']] = message['port']
                print(f"New peer added to the list: {message['host']}:{message['port']}")

        except Exception as e:
            print(f"Client encountered an error: {e}")
        finally:
            client_socket.close()

    def remove_peer(self, peer_host, peer_port):
        """ Removes the peer from the list """
        with self.lock:
            if peer_host in self.peers and self.peers[peer_host] == peer_port:
                del self.peers[peer_host]
                print(f"Peer {peer_host}:{peer_port} has been removed from the list.")
            else:
                print(f"Could not find peer {peer_host}:{peer_port}.")

    def join_network(self, peer_host, peer_port): # Args: address and port of any network member
        try:
            print(f"Trying to receive list of peers from {peer_host}:{peer_port}...")
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((peer_host, peer_port))
            message = json.dumps({'type': 'JOIN', 'host': self.host, 'port': self.port})
            client_socket.send(message.encode('utf-8'))

            # Receive the list of the known peers
            data = client_socket.recv(1024).decode('utf-8')
            response = json.loads(data)
            if response['type'] == 'PEERS':
                with self.lock:
                    self.peers.update(response['peers'])
                    self.peers[peer_host] = peer_port
                print(f"Received list of peers: {self.peers}")

        except Exception as e:
            print(f"Error connecting to {peer_host}:{peer_port}: {e}")
        finally:
            client_socket.close()

    def broadcast_new_peer(self, new_peer_host, new_peer_port):
        """ Broadcasts the new peer to the every other peer """
        with self.lock:
            for peer_host, peer_port in self.peers.items():
                if peer_host == new_peer_host and peer_port == new_peer_port:
                    continue
                try:
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect((peer_host, peer_port))
                    message = json.dumps({'type': 'NEW_PEER', 'host': new_peer_host, 'port': new_peer_port})
                    client_socket.send(message.encode('utf-8'))
                    client_socket.close()
                    print(f"Broadcasted the new peer {new_peer_host}:{new_peer_port} to {peer_host}:{peer_port}")
                except Exception as e:
                    print(f"Failure when trying to broadcast the new peer to {peer_host}:{peer_port}: {e}")

    def leave_network(self):
        """ Broadcasts to the other peers information that this peer leaves the network """
        with self.lock:
            for peer_host, peer_port in self.peers.items():
                try:
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect((peer_host, peer_port))
                    message = json.dumps({'type': 'LEAVE', 'host': self.host, 'port': self.port})
                    client_socket.send(message.encode('utf-8'))
                    client_socket.close()
                except Exception as e:
                    print(f"Failure when trying to notify {peer_host}:{peer_port} about leaving the network: {e}")

        self.is_running = False
        print(f"Node {self.host}:{self.port} left the network.")
        self.close_server()
    
    def close_server(self):
        self.is_running = False
        
        try:
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_socket.connect((self.host, self.port))
            temp_socket.close()
        except Exception as e:
            print(f"Error while trying to stop the server: {e}")

        print(f"Server on {self.host}:{self.port} has been closed.")
