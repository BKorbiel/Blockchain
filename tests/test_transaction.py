import unittest
import sys
from io import StringIO
from Wallet import Wallet
from Transaction import Transaction

class TestTransaction(unittest.TestCase):
    def setUp(self):
        self.held_output = StringIO()
        sys.stdout = self.held_output

        self.wallet = Wallet()
        self.recipient_public_key = "DUMMY_RECIPIENT_KEY"
        self.transaction = Transaction(
            sender_public_key_bytes=self.wallet.get_public_key(),
            recipient_public_key=self.recipient_public_key,
            amount=10.0
        )

    def tearDown(self):
        sys.stdout = sys.__stdout__

    def test_initialization(self):
        self.assertEqual(self.transaction.sender_public_key_bytes, self.wallet.get_public_key())
        self.assertEqual(self.transaction.recipient_public_key, self.recipient_public_key)
        self.assertEqual(self.transaction.amount, 10)
        self.assertIsNone(self.transaction.signature)
        self.assertIsNotNone(self.transaction.timestamp)

    def test_sign_transaction(self):
        self.transaction.sign_transaction(self.wallet)
        self.assertIsNotNone(self.transaction.signature)

    def test_sign_transaction_invalid_wallet(self):
        otherWallet = Wallet()

        with self.assertRaises(Exception) as context:
            self.transaction.sign_transaction(otherWallet)
        self.assertEqual(str(context.exception), "Cannot sign transaction for other wallets!")

    def test_is_valid(self):
        self.transaction.sign_transaction(self.wallet)
        self.assertTrue(self.transaction.is_valid())

    def test_is_not_valid_unsigned(self):
        with self.assertRaises(Exception) as context:
            self.transaction.is_valid()
        self.assertEqual(str(context.exception), "Transaction is not signed")

    def test_is_not_valid_negative_amount(self):
        self.transaction.amount = -5
        with self.assertRaises(Exception) as context:
            self.transaction.is_valid()
        self.assertEqual(str(context.exception), "Amount can not be negative")

    def test_to_json(self):
        self.transaction.sign_transaction(self.wallet)
        json_data = self.transaction.to_json()
        self.assertEqual(json_data['sender_public_key'], self.wallet.get_public_key().decode('utf-8'))
        self.assertEqual(json_data['recipient_public_key'], self.recipient_public_key)
        self.assertEqual(json_data['amount'], 10)
        self.assertIsNotNone(json_data['signature'])

    def test_from_json(self):
        self.transaction.sign_transaction(self.wallet)
        json_data = self.transaction.to_json()
        new_transaction = Transaction.from_json(json_data)
        self.assertEqual(self.transaction, new_transaction)

    def test_str_representation(self):
        expected_str = (f"  Sender: {self.wallet.get_public_key()}\n"
                        f"  Recipient: {self.recipient_public_key}\n"
                        f"  Amount: 10.0\n"
                        f"  Signature: Unsigned\n"
                        f"  Timestamp: {self.transaction.timestamp}\n")
        self.assertEqual(str(self.transaction), expected_str)
    

