import json
from Wallet import Wallet

class Transaction:
    def __init__(self, sender_public_key_bytes, recipient_public_key, amount, signature=None):
        self.sender_public_key_bytes = sender_public_key_bytes
        self.recipient_public_key = recipient_public_key
        self.amount = amount
        self.signature = signature

    def sign_transaction(self, wallet):
        if wallet.get_public_key() != self.sender_public_key_bytes:
            raise Exception("Cannot sign transaction for other wallets!")
        transaction_data = str(self.sender_public_key_bytes) + str(self.recipient_public_key) + str(self.amount)
        self.signature = wallet.sign_transaction(transaction_data)

    def is_valid(self):
        if self.amount < 0:
            raise Exception("Amount can not be negative")
            return False
        if self.signature is None:
            raise Exception("Transaction is not signed")
            return False
        transaction_data = str(self.sender_public_key_bytes) + str(self.recipient_public_key) + str(self.amount)
        return Wallet.verify_signature(self.sender_public_key_bytes, transaction_data, self.signature)
    
    def __str__(self):
        return (f"  Sender: {self.sender_public_key_bytes}\n"
                f"  Recipient: {self.recipient_public_key}\n"
                f"  Amount: {self.amount}\n"
                f"  Signature: {self.signature if self.signature else 'Unsigned'}\n")
