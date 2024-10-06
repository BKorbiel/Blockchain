import socket
import threading
import json
import time
from Blockchain import Blockchain
from Transaction import Transaction

class Server:
    def __init__(self, p2p_node):
        self.p2p_node = p2p_node
        self.is_running = True
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.start()
    
    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.p2p_node.ip_address, self.p2p_node.port))
        server_socket.listen(5)
        print(f"Server started on port {self.p2p_node.ip_address}:{self.p2p_node.port}")

        while self.is_running:
            try:
                client_socket, addr = server_socket.accept()
                threading.Thread(target=self.handle_request, args=(client_socket,)).start()
            except Exception as e:
                print(f"Server encountered an error: {e}")
                break
    
    def handle_request(self, client_socket):
        try:
            data = client_socket.recv(8192).decode('utf-8')
            if not data:
                return

            message = json.loads(data)

            if message['type'] == 'PEERS_REQ': # Request for the list of peers
                response = json.dumps({'type': 'PEERS', 'peers': self.p2p_node.peers})
                client_socket.send(response.encode('utf-8'))

            elif message['type'] == 'LEAVE':
                # Peer leaves the network
                self.p2p_node.remove_peer(message['ip_address'], message['port'])

            elif message['type'] == 'NEW_PEER':
                # New peer joined the network, respond with the current chain of blocks
                response = json.dumps({
                    'type': 'BLOCKCHAIN',
                    'blockchain': [block.to_json() for block in self.p2p_node.blockchain.chain]
                })
                client_socket.send(response.encode('utf-8'))
                self.p2p_node.add_peer(message['ip_address'], message['port'])
            
            elif message['type'] == 'NEW_TRANSACTION':
                # Received new transaction
                transaction = Transaction.from_json(message['transaction'])
                self.p2p_node.blockchain.add_new_transaction(transaction)

            elif message['type'] == 'BLOCKCHAIN':
                self.p2p_node.blockchain.compare_replace(message['blockchain'])

        except Exception as e:
            print(f"Server encountered an error: {e}")
        finally:
            client_socket.close()

    def close(self):
        self.is_running = False
        try:
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_socket.connect((self.p2p_node.ip_address, self.p2p_node.port))
            temp_socket.close()
        except Exception as e:
            print(f"Error while trying to stop the server: {e}")

        print(f"Server on {self.p2p_node.ip_address}:{self.p2p_node.port} has been closed.")

class Client:
    def __init__(self, p2p_node):
        self.p2p_node = p2p_node
    
    def request_peers(self, peer_ip_addr, peer_port):
        try:
            print(f"Trying to receive list of peers from {peer_ip_addr}:{peer_port}...")
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((peer_ip_addr, peer_port))
            message = json.dumps({'type': 'PEERS_REQ'})
            client_socket.send(message.encode('utf-8'))

            # Receive the list of the known peers
            data = client_socket.recv(8192).decode('utf-8')
            response = json.loads(data)
            if response['type'] == 'PEERS':
                self.p2p_node.update_peers(response['peers'])

        except Exception as e:
            print(f"Error connecting to {peer_ip_addr}:{peer_port}: {e}")
        finally:
            client_socket.close()

    def request_chain(self, peer_ip_addr, peer_port):
        try:
            # Send information about new peer in the network
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((peer_ip_addr, peer_port))
            message = json.dumps({'type': 'NEW_PEER', 'ip_address': self.p2p_node.ip_address, 'port': self.p2p_node.port})
            client_socket.send(message.encode('utf-8'))

            # Receive copy of the blockchain
            data = client_socket.recv(8192).decode('utf-8')
            response = json.loads(data)
            if response['type'] == 'BLOCKCHAIN':
                client_socket.close()
                return response['blockchain']

            client_socket.close()
            return []

        except Exception as e:
            print(f"Failure when trying to request chain from {peer_ip_addr}:{peer_port}: {e}")
            return []
            
    def send_message_to_peer(self, message, peer_ip_addr, peer_port):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((peer_ip_addr, peer_port))
            client_socket.send(message.encode('utf-8'))
            client_socket.close()
            print(f"Sent message {message} to {peer_ip_addr}:{peer_port}")
        except Exception as e:
            print(f"Failure when trying to send the message to {peer_ip_addr}:{peer_port}: {e}")

class P2PNode:
    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.peers = {}
        self.lock = threading.Lock()
        self.server = Server(self)
        self.client = Client(self)
        self.blockchain = Blockchain(difficulty = 4, broadcast_cb = self.broadcast_blockchain)
    
    def join_network(self, peer_ip_addr, peer_port):
        with self.lock:
            self.peers[peer_ip_addr] = peer_port
        self.client.request_peers(peer_ip_addr, peer_port)
        self.connect_and_sync()
    
    def connect_and_sync(self):
        """ Broadcasts the new peer to the every other peer and select the longest chain of blocks """
        self.blockchain.chain = []
        with self.lock:
            for peer_ip_addr, peer_port in self.peers.items():
                peer_chain = self.client.request_chain(peer_ip_addr, peer_port)
                print(f"{peer_ip_addr} responded with chain: {peer_chain}")

                self.blockchain.compare_replace(peer_chain)
    
    def update_peers(self, peers):
        with self.lock:
            self.peers.update(peers)
        print(f"Updated list of peers: {self.peers}")
    
    def add_peer(self, ip_address, port):
        with self.lock:
            self.peers[ip_address] = port
        print(f"New peer added to the list: {ip_address}:{port}")
    
    def remove_peer(self, ip_address, port):
        """ Removes the peer from the list """
        with self.lock:
            if ip_address in self.peers and self.peers[ip_address] == port:
                del self.peers[ip_address]
                print(f"Peer {ip_address}:{port} has been removed from the list.")
            else:
                print(f"Could not find peer {ip_address}:{port}.")
    
    def leave_network(self):
        """ Broadcasts to the other peers information that this peer leaves the network """
        message = json.dumps({'type': 'LEAVE', 'ip_address': self.ip_address, 'port': self.port})
        with self.lock:
            for peer_ip_addr, peer_port in self.peers.items():
                self.client.send_message_to_peer(message, peer_ip_addr, peer_port)

        self.server.close()
    
    def add_new_transaction(self, transaction):
        self.blockchain.add_new_transaction(transaction)
        
        # Broadcast new transaction
        message = json.dumps({'type': 'NEW_TRANSACTION', 'transaction': transaction.to_json()})
        with self.lock:
            for peer_ip_addr, peer_port in self.peers.items():
                self.client.send_message_to_peer(message, peer_ip_addr, peer_port)
    
    def broadcast_blockchain(self):
        # Broadcast own blockchain copy
        message = json.dumps({
            'type': 'BLOCKCHAIN',
            'blockchain': [block.to_json() for block in self.blockchain.chain]
        })
        with self.lock:
            for peer_ip_addr, peer_port in self.peers.items():
                self.client.send_message_to_peer(message, peer_ip_addr, peer_port)
