import unittest
from unittest.mock import patch, MagicMock
from Blockchain import Blockchain
from Block import Block
from Transaction import Transaction
import sys
from io import StringIO

class TestBlockchain(unittest.TestCase):
    
    def setUp(self):
        self.held_output = StringIO()
        sys.stdout = self.held_output

        self.difficulty = 2
        self.broadcast_cb = MagicMock()
        self.blockchain = Blockchain(self.difficulty, self.broadcast_cb)
    
    def tearDown(self):
        sys.stdout = sys.__stdout__

    @patch('Block.Block.from_json')
    @patch('Blockchain.Blockchain.is_chain_valid')
    def test_compare_replace_valid_chain(self, mock_is_chain_valid, mock_from_json):
        new_chain_json = [{'index': 1}, {'index': 2}]
        mock_from_json.return_value = MagicMock(spec=Block)
        mock_from_json.return_value.data = []
        mock_is_chain_valid.return_value = True

        self.blockchain.compare_replace(new_chain_json)

        self.assertEqual(len(self.blockchain.chain), 2)
        mock_is_chain_valid.assert_called_once()

    @patch('Block.Block.from_json')
    @patch('Blockchain.Blockchain.is_chain_valid')
    def test_compare_replace_invalid_chain(self, mock_is_chain_valid, mock_from_json):
        new_chain_json = [{'index': 1}, {'index': 2}]
        mock_from_json.return_value = MagicMock(spec=Block)
        mock_is_chain_valid.return_value = False

        self.blockchain.compare_replace(new_chain_json)

        self.assertEqual(len(self.blockchain.chain), 1)  # Genesis block only
        mock_is_chain_valid.assert_called_once()
        self.broadcast_cb.assert_not_called()

    @patch('Block.Block.from_json')
    @patch('Blockchain.Blockchain.is_chain_valid')
    def test_compare_replace_equal_length(self, mock_is_chain_valid, mock_from_json):
        new_chain_json = [{'index': 1}]

        self.blockchain.compare_replace(new_chain_json)

        self.assertEqual(len(self.blockchain.chain), 1)  # Genesis block only
        mock_from_json.assert_not_called()
        mock_is_chain_valid.assert_not_called()
        self.broadcast_cb.assert_not_called()

    def test_add_new_transaction_valid(self):
        mock_transaction = MagicMock(spec=Transaction)
        mock_transaction.is_valid = lambda : True

        self.blockchain.add_new_transaction(mock_transaction)

        self.assertIn(mock_transaction, self.blockchain.mempool)
        self.assertIsNone(self.blockchain.currently_mined_block)

    def test_add_new_transaction_invalid(self):
        mock_transaction = MagicMock(spec=Transaction)
        mock_transaction.is_valid = lambda : False

        self.blockchain.add_new_transaction(mock_transaction)

        self.assertNotIn(mock_transaction, self.blockchain.mempool)
        self.assertIsNone(self.blockchain.currently_mined_block)
    
    @patch('Block.Block')
    @patch('Blockchain.Blockchain.start_mining')
    def test_add_new_transactions_and_create_block(self, mock_start_mining, mock_block_class):
        mock_transaction = MagicMock(spec=Transaction)
        mock_transaction.is_valid = lambda : True
        mock_block_class.return_value = MagicMock(spec=Block)

        for i in range(5):
            self.blockchain.add_new_transaction(mock_transaction)

        self.assertIn(mock_transaction, self.blockchain.mempool)
        self.assertIsNotNone(self.blockchain.currently_mined_block)
        mock_start_mining.assert_called_once()

    def test_start_mining_valid_block(self):
        last_block = self.blockchain.chain[-1]
        mock_block = MagicMock(spec=Block)
        mock_block.data = []
        self.blockchain.currently_mined_block = mock_block
        mock_block.mine_block = lambda difficulty: True

        self.blockchain.start_mining(mock_block)

        mock_block.validate_block.assert_called_once_with(last_block, self.blockchain.difficulty)

        self.broadcast_cb.assert_called_once()

if __name__ == '__main__':
    unittest.main()
