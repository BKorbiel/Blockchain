import hashlib
import json
import time
from Transaction import Transaction

class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash = None, nonce = None):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.stop_mining = False
        self.hash = hash
        self.nonce = nonce

        if self.nonce is None:
            self.nonce = 0 # Proof of Work
        
        if self.hash is None:
            self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        data_str = ''.join(map(str, self.data))
        value = (str(self.index) + str(self.previous_hash) +
                 str(self.timestamp) + data_str + str(self.nonce))
        return hashlib.sha256(value.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
            if self.stop_mining:
                print("Mining stopped.")
                return False
            time.sleep(0)
        print("Mining finished.")
        return True

    def to_json(self):
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'data': [transaction.to_json() for transaction in self.data],
            'hash': self.hash,
            'nonce': self.nonce
        }

    def __str__(self):
        block_str = f" Index: {self.index} | Previous hash: {self.previous_hash} | Ts: {self.timestamp}\n | PoW: {self.nonce} | Hash: {self.hash}\n"
        block_str += " Transactions:\n"
        for i in range(0, len(self.data)):
            block_str += f"  Transaction #{i}:\n"
            block_str += str(self.data[i])
        return block_str

    @staticmethod
    def from_json(block_json):
        nonce = block_json.get('nonce', None)
        hash = block_json.get('hash', None)
        transactions = [Transaction.from_json(transaction) for transaction in block_json['data']]

        return Block(
            index = block_json['index'],
            previous_hash = block_json['previous_hash'],
            timestamp = block_json['timestamp'],
            data = transactions,
            hash = hash,
            nonce = nonce
        )

    def validate_block(self, previous_block, difficulty):
        if self.previous_hash != previous_block.hash:
            return False

        target = "0" * difficulty
        if self.hash[:difficulty] != target:
            return False

        if self.hash != self.calculate_hash():
            return False

        return True
