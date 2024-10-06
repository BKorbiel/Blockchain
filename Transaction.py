import json
import time
from Wallet import Wallet

class Transaction:
    def __init__(self, sender_public_key_bytes, recipient_public_key, amount, signature=None, timestamp=None):
        self.sender_public_key_bytes = sender_public_key_bytes
        self.recipient_public_key = recipient_public_key
        self.amount = amount
        self.signature = signature
        self.timestamp = timestamp
        
        if self.timestamp is None:
            self.timestamp = time.time()

    def sign_transaction(self, wallet):
        if wallet.get_public_key() != self.sender_public_key_bytes:
            raise Exception("Cannot sign transaction for other wallets!")
        transaction_data = str(self.sender_public_key_bytes) + str(self.recipient_public_key) + str(self.amount) + str(self.timestamp)
        self.signature = wallet.sign_transaction(transaction_data)

    def is_valid(self):
        if self.amount < 0:
            raise Exception("Amount can not be negative")
            return False
        if self.signature is None:
            raise Exception("Transaction is not signed")
            return False
        transaction_data = str(self.sender_public_key_bytes) + str(self.recipient_public_key) + str(self.amount) + str(self.timestamp)
        return Wallet.verify_signature(self.sender_public_key_bytes, transaction_data, self.signature)

    def to_json(self):
        return {
            'sender_public_key': self.sender_public_key_bytes.decode('utf-8'),
            'recipient_public_key': self.recipient_public_key,
            'amount': self.amount,
            'signature': self.signature.hex() if self.signature else None,
            'timestamp': self.timestamp
        }
    
    def __str__(self):
        return (f"  Sender: {self.sender_public_key_bytes}\n"
                f"  Recipient: {self.recipient_public_key}\n"
                f"  Amount: {self.amount}\n"
                f"  Signature: {self.signature if self.signature else 'Unsigned'}\n"
                f"  Timestamp: {self.timestamp}\n")

    @staticmethod
    def from_json(transaction_json):
        transaction = Transaction(
            sender_public_key_bytes=transaction_json['sender_public_key'].encode('utf-8'),
            recipient_public_key=transaction_json['recipient_public_key'],
            amount=transaction_json['amount'],
            timestamp=transaction_json['timestamp']
        )
        if transaction_json['signature']:
            transaction.signature = bytes.fromhex(transaction_json['signature'])
        return transaction

    def __eq__(self, other):
        if isinstance(other, Transaction):
            return (self.sender_public_key_bytes == other.sender_public_key_bytes and
                    self.recipient_public_key == other.recipient_public_key and
                    self.amount == other.amount and
                    self.timestamp == other.timestamp)
        return False
