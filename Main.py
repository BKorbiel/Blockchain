import socket
import sys
from Wallet import Wallet
from Network import P2PNode
from Blockchain import Blockchain
from Transaction import Transaction
from Block import Block

class Main:
    def main(self):
        self.setup_interface()
        
        while self.menu() == True:
            pass

        self.exit()

    def exit(self):
        self.node.leave_network()
        print("Program finished.")

    def menu(self):
        print("\nMenu:")
        print("1 - Create a new transaction")
        print("2 - View current blockchain")
        print("3 - Exit")
        selection = input("Enter 1, 2 or 3: ")

        if selection == "3":
            return False
        
        if selection == "2":
            print(str(self.node.blockchain))
            return True

        if selection == "1":
            recipient_public_key = input("Input recipient public key: ")
            amount = int(input("Input amount: "))
            self.create_new_transaction(recipient_public_key, amount)
            return True
    
    def setup_interface(self):
        # Get IP address and port for the server part of the p2p node
        server_ip = input("Input your IP address (127.0.0.1 by default): ") or "127.0.0.1"
        server_port = input("Input port (5000 by default): ")
        server_port = int(server_port) if server_port else 5000

        # Get IP address and port of an existing node (if P2P network already exists)
        is_first_node = input("Are you the first peer in the blockchain? (yes/no): ").lower() == "yes"
        peer_ip = None
        peer_port = None
        if not is_first_node:
            peer_ip = input("Input any other peer's IP address: ")
            peer_port = input("Input port: ")
            peer_port = int(peer_port)

        # Getting public and private key
        private_key = None
        public_key = None
        use_existing_wallet = input("Do you have existing public and private keys? (yes/no): ").lower() == "yes"
        if use_existing_wallet:
            print("Please enter your private key (press Enter, Ctrl+Z and again Enter to finish):")
            private_key = sys.stdin.read()
            print("Please enter your public key (press Enter, Ctrl+Z and again Enter to finish):")
            public_key = sys.stdin.read()
        
        self.setup(server_ip, server_port, peer_ip, peer_port, private_key, public_key)

    def setup(self, server_ip, server_port, peer_ip, peer_port, private_key, public_key):
        self.node = P2PNode(server_ip, server_port)
        if (peer_ip and peer_port):
            self.node.join_network(peer_ip, peer_port)
        
        self.wallet = Wallet(private_key, public_key)
    
    def create_new_transaction(self, recipient_public_key, amount):
        transaction = Transaction(sender_public_key_bytes=self.wallet.get_public_key(), recipient_public_key=recipient_public_key, amount=amount)
        transaction.sign_transaction(self.wallet)

        if transaction.is_valid():
            print("Adding the new transaction to the blockchain and broadcasting it...")
            self.node.add_new_transaction(transaction)
        else:
            print("Transaction is invalid.")

if __name__ == "__main__":
    app = Main()
    app.main()
    
