import socket
import threading
import json
import time

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
            data = client_socket.recv(1024).decode('utf-8')
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
                # New peer joined the network, update the list of peers
                self.p2p_node.add_peer(message['ip_address'], message['port'])

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
            data = client_socket.recv(1024).decode('utf-8')
            response = json.loads(data)
            if response['type'] == 'PEERS':
                self.p2p_node.update_peers(response['peers'])

        except Exception as e:
            print(f"Error connecting to {peer_ip_addr}:{peer_port}: {e}")
        finally:
            client_socket.close()

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
    
    def join_network(self, peer_ip_addr, peer_port):
        with self.lock:
            self.peers[peer_ip_addr] = peer_port
        self.client.request_peers(peer_ip_addr, peer_port)
        self.broadcast_new_peer()
    
    def broadcast_new_peer(self):
        """ Broadcasts the new peer to the every other peer """
        message = json.dumps({'type': 'NEW_PEER', 'ip_address': self.ip_address, 'port': self.port})
        with self.lock:
            for peer_ip_addr, peer_port in self.peers.items():
                self.client.send_message_to_peer(message, peer_ip_addr, peer_port)
    
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
    
def example():
    # Creating three nodes for simulation with different host IPs
    node1 = P2PNode('127.0.0.1', 5000)
    node2 = P2PNode('127.0.0.2', 5001)
    node3 = P2PNode('127.0.0.3', 5002)

    # Node2 connects to Node1 and receives the list of peers
    node2.join_network('127.0.0.1', 5000)

    time.sleep(1)

    # Node3 connects to Node2 and receives the list of peers (which includes Node1)
    node3.join_network('127.0.0.2', 5001)

    # Simulation delay to allow peer exchange
    time.sleep(5)

    # Nodes leave the network
    node2.leave_network()

    time.sleep(1)

    node1.leave_network()

    node3.leave_network()

example()