import unittest
import sys
from io import StringIO
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from Wallet import Wallet

class TestWallet(unittest.TestCase):

    def setUp(self):
        self.held_output = StringIO()
        sys.stdout = self.held_output

        self.wallet = Wallet()
    
    def tearDown(self):
        sys.stdout = sys.__stdout__

    def test_key_generation(self):
        """Test that the wallet generates a public and private key."""
        self.assertIsNotNone(self.wallet.private_key)
        self.assertIsNotNone(self.wallet.public_key)

        public_key_bytes = self.wallet.get_public_key()
        self.assertIsInstance(public_key_bytes, bytes)

        private_key_bytes = self.wallet.get_private_key()
        self.assertIsInstance(private_key_bytes, bytes)

    def test_sign_transaction(self):
        """Test that a transaction can be signed."""
        transaction_data = "test_transaction"
        signature = self.wallet.sign_transaction(transaction_data)
        self.assertIsInstance(signature, bytes)

    def test_verify_signature(self):
        """Test that a valid signature can be verified."""
        transaction_data = "test_transaction"
        signature = self.wallet.sign_transaction(transaction_data)
        public_key_bytes = self.wallet.get_public_key()
        
        is_valid = Wallet.verify_signature(public_key_bytes, transaction_data, signature)
        self.assertTrue(is_valid)

    def test_verify_signature_invalid(self):
        """Test that an invalid signature cannot be verified."""
        transaction_data = "test_transaction"
        signature = self.wallet.sign_transaction(transaction_data)

        fake_transaction_data = "fake_transaction"

        public_key_bytes = self.wallet.get_public_key()

        is_valid = Wallet.verify_signature(public_key_bytes, fake_transaction_data, signature)
        self.assertFalse(is_valid)

    def test_load_keys(self):
        """Test loading private and public keys from strings."""
        private_key_bytes = self.wallet.get_private_key()
        public_key_bytes = self.wallet.get_public_key()

        # Create a new wallet from existing keys
        loaded_wallet = Wallet(private_key=private_key_bytes.decode('utf-8'),
                                public_key=public_key_bytes.decode('utf-8'))

        # Ensure loaded keys match the original keys
        self.assertEqual(self.wallet.get_public_key(), loaded_wallet.get_public_key())
        self.assertEqual(self.wallet.get_private_key(), loaded_wallet.get_private_key())

if __name__ == '__main__':
    unittest.main()
