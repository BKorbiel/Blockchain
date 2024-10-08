from Main import Main
import time
from Wallet import Wallet

def example():
    # Creating three peers for simulation
    peer1 = Main()
    peer2 = Main()
    peer3 = Main()

    # Peer1 setup - the first peer in the network
    peer1.setup(
        server_ip='127.0.0.1', 
        server_port=5000, 
        peer_ip=None, # This peer is the first in the network so it doesn't provided any other peer's ip
        peer_port=None, 
        private_key=None, # Keys are not provided, so they'll be generated automatically 
        public_key=None)

    time.sleep(1)

    # Peer2 joins the network
    peer2.setup(
        server_ip='127.0.0.2', 
        server_port=5001, 
        peer_ip='127.0.0.1', # Network already exists, so any peer's ip and host have to be provided
        peer_port=5000, 
        private_key=None, # Keys are not provided, so they'll be generated automatically 
        public_key=None)

    time.sleep(1)

    # Peer1 creates 3 transactions
    for i in range(0, 3):
        peer1.create_new_transaction("DUMMY_RECIPIENT", 15)
        time.sleep(0.1)
    
    time.sleep(1)
    # Peer2 adds 2 transactions
    peer2.create_new_transaction("DUMMY_RECIPIENT", 15)
    time.sleep(1)
    peer2.create_new_transaction("DUMMY_RECIPIENT", 15)

    # Both Peer1 and Peer2 have 5 transactions in mempool, so they start to mine a new block
    # When they finish, they will broadcast their own blockchain copy. 
    # If one of these nodes receives new (valid and longer) blockchain while mining, it'll stop mining
    # Mempools are updated

    # Peer2 broadcasts new transaction, Peer1 and Peer2 add it to their mempool
    peer2.create_new_transaction("DUMMY_RECIPIENT", 100)
    time.sleep(1)

    # Peer3 joins the network. It'll receive blockchains from Peer1 and Peer2 and select the longest
    wallet = Wallet()
    peer3.setup(
        server_ip='127.0.0.3', 
        server_port=5002, 
        peer_ip='127.0.0.1', # Network already exists, so any peer's ip and host have to be provided
        peer_port=5000, 
        private_key=wallet.get_private_key().decode('utf-8'), # Keys are provided (as strings)
        public_key=wallet.get_public_key().decode('utf-8'))
    
    time.sleep(1)
    # Peer3 creates 4 transactions
    for i in range(0, 4):
        time.sleep(0.1)
        peer3.create_new_transaction("DUMMY_RECIPIENT", 15)
    # Again, Peer1 and Peer2 now have 5 transactions in their mempool, so they start to mine a new block
    # Peer3 has only 4 transactions in it's mempool, so it doesn't mine yet

    # Peer3'll receive a new blockchain copy from Peer1 or Peer2 (or both of them) and accept it if it's valid and 
    # longer than it's current copy. Then it's mempool'll be adjusted (all transactions that are already in any 
    # block will be removed from the mempool)
    time.sleep(1)
    # Nodes leave the network
    peer1.exit()
    time.sleep(1)
    peer2.exit()
    time.sleep(1)
    peer3.exit()

if __name__ == "__main__":
    example()