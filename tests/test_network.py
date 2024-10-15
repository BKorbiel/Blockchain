import unittest
from unittest.mock import patch, MagicMock
import json
from Network import Server, Client, P2PNode
from Blockchain import Blockchain
from Transaction import Transaction
import sys
from io import StringIO

class TestServer(unittest.TestCase):
    @patch('threading.Thread')
    def setUp(self, mock_thread):
        self.held_output = StringIO()
        sys.stdout = self.held_output

        self.mock_blockchain = MagicMock()
        self.mock_blockchain.data = []
        self.mock_client_socket = MagicMock()
        self.mock_p2p_node = MagicMock()
        self.mock_p2p_node.blockchain = self.mock_blockchain
        self.server = Server(self.mock_p2p_node)
    
    def tearDown(self):
        sys.stdout = sys.__stdout__

    @patch('socket.socket')
    def test_handle_request_peers_req(self, mock_socket):
        self.mock_client_socket.recv.return_value = json.dumps({'type': 'PEERS_REQ'}).encode('utf-8')
        self.server.p2p_node.peers = {'127.0.0.1': 5000}
        
        self.server.handle_request(self.mock_client_socket)

        self.mock_client_socket.send.assert_called_once_with(
            json.dumps({'type': 'PEERS', 'peers': {'127.0.0.1': 5000}}).encode('utf-8')
        )

    @patch('socket.socket')
    def test_handle_request_new_peer(self, mock_socket):
        self.mock_client_socket.recv.return_value = json.dumps({'type': 'NEW_PEER', 'ip_address': '192.168.1.1', 'port': 5001}).encode('utf-8')

        self.server.handle_request(self.mock_client_socket)

        self.mock_client_socket.send.assert_called_once_with(
            json.dumps({
                    'type': 'BLOCKCHAIN',
                    'blockchain': []
            }).encode('utf-8')
        )
        self.mock_p2p_node.add_peer.assert_called_once_with('192.168.1.1', 5001)

    @patch('socket.socket')
    def test_handle_request_new_transaction(self, mock_socket):
        transaction_data = {'amount': 10, 'sender_public_key': '123456', 'recipient_public_key': '654321', 'timestamp': 15, 'signature': ''}
        self.mock_client_socket.recv.return_value = json.dumps({'type': 'NEW_TRANSACTION', 'transaction': transaction_data}).encode('utf-8')
        self.mock_p2p_node.blockchain.add_new_transaction = MagicMock()

        self.server.handle_request(self.mock_client_socket)

        self.mock_p2p_node.blockchain.add_new_transaction.assert_called_once_with(Transaction.from_json(transaction_data))

class TestClient(unittest.TestCase):
    def setUp(self):
        self.held_output = StringIO()
        sys.stdout = self.held_output

        self.mock_blockchain = MagicMock()
        self.mock_blockchain.data = []
        self.mock_client_socket = MagicMock()
        self.mock_p2p_node = MagicMock()
        self.mock_p2p_node.blockchain = self.mock_blockchain
        self.client = Client(self.mock_p2p_node)
    
    def tearDown(self):
        sys.stdout = sys.__stdout__

    @patch('socket.socket')
    def test_request_peers(self, mock_socket):
        self.mock_client_socket.recv.return_value = json.dumps({'type': 'PEERS', 'peers': {'192.168.1.4': 5002}}).encode('utf-8')
        mock_socket.return_value = self.mock_client_socket
        
        self.client.request_peers('192.168.1.1', 5001)

        self.mock_p2p_node.update_peers.assert_called_once_with({'192.168.1.4': 5002})

    @patch('socket.socket')
    def test_request_chain(self, mock_socket):
        self.mock_client_socket.recv.return_value = json.dumps({'type': 'BLOCKCHAIN', 'blockchain': []}).encode('utf-8')
        mock_socket.return_value = self.mock_client_socket

        blockchain = self.client.request_chain('192.168.1.1', 5001)

        self.assertEqual(blockchain, [])
        
    @patch('socket.socket')
    def test_send_message_to_peer(self, mock_socket):
        mock_socket.return_value = self.mock_client_socket

        self.client.send_message_to_peer('Hello', '192.168.1.1', 5001)

        self.mock_client_socket.send.assert_called_once_with('Hello'.encode('utf-8'))

class TestP2PNode(unittest.TestCase):
    @patch('Network.Client')
    @patch('Network.Server')
    def setUp(self, mock_server, mock_client):
        self.held_output = StringIO()
        sys.stdout = self.held_output

        self.mock_client_instance = mock_client.return_value
        self.mock_p2p_node = P2PNode('127.0.0.1', 5000)
    
    def tearDown(self):
        sys.stdout = sys.__stdout__

    @patch('Network.Client')
    @patch('Network.Server')
    def test_join_network(self, mock_server, mock_client):
        self.mock_client_instance.request_peers.return_value = None

        self.mock_p2p_node.join_network('192.168.1.1', 5001)

        self.mock_client_instance.request_peers.assert_called_once_with('192.168.1.1', 5001)

    @patch('Network.Client')
    @patch('Network.Server')
    def test_leave_network(self, mock_server, mock_client):
        self.mock_client_instance.send_message_to_peer = MagicMock()

        self.mock_p2p_node.leave_network()

        for peer_ip_addr, peer_port in self.mock_p2p_node.peers.items():
            self.mock_client_instance.send_message_to_peer.assert_any_call(
                json.dumps({'type': 'LEAVE', 'ip_address': '127.0.0.1', 'port': 5000}),
                peer_ip_addr,
                peer_port
            )

if __name__ == '__main__':
    unittest.main()
