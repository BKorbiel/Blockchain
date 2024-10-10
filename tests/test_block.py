import unittest
import time
from Wallet import Wallet
from Transaction import Transaction
from Block import Block
from unittest.mock import patch, MagicMock
import sys
from io import StringIO

class TestBlock(unittest.TestCase):

    def setUp(self):
        self.held_output = StringIO()
        sys.stdout = self.held_output

        self.mock_wallet = MagicMock()
        self.mock_wallet.get_public_key.return_value = b"mock_public_key"
        
        self.mock_transaction = MagicMock()
        self.mock_transaction.to_json.return_value = {'mock': 'data'}
        
        self.previous_block = Block(
            index=0,
            previous_hash="0",
            timestamp=time.time(),
            data=[]
        )
        self.block = Block(
            index=1,
            previous_hash=self.previous_block.hash,
            timestamp=time.time(),
            data=[self.mock_transaction]
        )
    
    def tearDown(self):
        sys.stdout = sys.__stdout__

    def test_calculate_hash(self):
        block_hash = self.block.calculate_hash()
        self.assertIsNotNone(block_hash)
        self.assertEqual(len(block_hash), 64)  # SHA-256 produces a 64 character hex string

    def test_mine_block(self):
        difficulty = 2
        self.assertTrue(self.block.mine_block(difficulty))
        self.assertTrue(self.block.hash.startswith("0" * difficulty))

    def test_mine_block_stopped(self):
        difficulty = 2
        self.block.stop_mining = True  # Simulate stopping the mining
        self.assertFalse(self.block.mine_block(difficulty))

    def test_to_json(self):
        self.block.mine_block(2)
        json_data = self.block.to_json()
        self.assertEqual(json_data['index'], self.block.index)
        self.assertEqual(json_data['previous_hash'], self.block.previous_hash)
        self.assertEqual(json_data['timestamp'], self.block.timestamp)
        self.assertEqual(len(json_data['data']), 1)
        self.assertEqual(json_data['data'][0], self.mock_transaction.to_json())
        self.assertEqual(json_data['hash'], self.block.hash)
        self.assertEqual(json_data['nonce'], self.block.nonce)

    @patch('Transaction.Transaction.from_json')
    def test_from_json(self, mock_transaction_from_json):
        mock_transaction_from_json.return_value = self.mock_transaction

        self.block.mine_block(2)
        block_json = self.block.to_json()
        new_block = Block.from_json(block_json)
        self.assertEqual(self.block.index, new_block.index)
        self.assertEqual(self.block.previous_hash, new_block.previous_hash)
        self.assertEqual(self.block.timestamp, new_block.timestamp)
        self.assertEqual(len(self.block.data), len(new_block.data))
        self.assertEqual(self.mock_transaction, new_block.data[0])
        self.assertEqual(self.block.hash, new_block.hash)

    def test_validate_block(self):
        self.block.mine_block(2)
        self.assertTrue(self.block.validate_block(self.previous_block, 2))

    def test_validate_block_invalid_previous_hash(self):
        self.block.previous_hash = "invalid_hash"
        self.block.mine_block(2)
        self.assertFalse(self.block.validate_block(self.previous_block, 2))

    def test_validate_block_invalid_difficulty(self):
        while self.block.hash[1] == '0':
            self.block.mine_block(1)
        self.assertFalse(self.block.validate_block(self.previous_block, 2))

    def test_validate_block_invalid_hash(self):
        self.block.hash = "00_invalid_hash"
        self.assertFalse(self.block.validate_block(self.previous_block, 2))

if __name__ == '__main__':
    unittest.main()
